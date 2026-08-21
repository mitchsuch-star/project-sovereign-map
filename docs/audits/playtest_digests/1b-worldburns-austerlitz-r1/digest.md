# Playtest digest — 1b-worldburns-austerlitz-r1

seed `austerlitz` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "decline", "capture": "plunder", "estate": "confiscate", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "dismiss", "petition": "first_enabled", "interrupt": "first", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `declare war on Prussia` → ✓ Choose your war purpose against Prussia.
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on Prussia. Our threat level stands at 69 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, Prussia → proceed
  - POPUP diplomatic_dialogue: proposal_confirm → ally_entry_proceed_without
  - POPUP proposal_result: France declares war on Prussia! Holland follows France into the war against Prussia! KingdomOfItaly follows France into the war against Prussia! Switzerland follows France into the war against Prussia! → display-only
- CMD `declare war on Sweden` → ✓ Choose your war purpose against Sweden.
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on Sweden. Our threat level stands at 89 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, Sweden → proceed
  - POPUP diplomatic_dialogue: proposal_confirm → ally_entry_proceed_without
  - POPUP proposal_result: France declares war on Sweden! Holland follows France into the war against Sweden! KingdomOfItaly follows France into the war against Sweden! Switzerland follows France into the war against Sweden! → display-only
- CMD `declare war on Denmark` → ✓ Choose your war purpose against Denmark.
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on Denmark. Our threat level stands at 100 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, Denmark → proceed
  - POPUP diplomatic_dialogue: proposal_confirm → ally_entry_proceed_without
  - POPUP proposal_result: France declares war on Denmark! Holland follows France into the war against Denmark! KingdomOfItaly follows France into the war against Denmark! Switzerland follows France into the war against Denmark! → display-only
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 4 action(s) unused) Turn 2 begins!
- enemy phase: 2 actions, 2 attacks — [Shield] Massena is at his best with his back to the wall! (Child of Victory: +10% defense when outnumbered) · [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered)
  - ⚔ Archduke Charles (lost 4761) vs Massena (lost 5508) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Brunswick (lost 2192) vs Bernadotte (lost 5128) — Bernadotte's army has been badly mauled. Brunswick proved the stronger force today.
  - verbs: attack×2
- LEDGER treasury 2407 · net +2121 · provinces 28
- DISPATCH: Sire — Bernadotte was mauled at Franconia: 5,128 men lost in a single action.

## Turn 2 — Early October 1805
- CMD `declare war on Ottoman` → ✓ Choose your war purpose against Ottoman.
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on Ottoman. Our threat level stands at 97 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, Ottoman → proceed
  - POPUP diplomatic_dialogue: proposal_confirm → ally_entry_proceed_without
  - POPUP proposal_result: France declares war on Ottoman! Holland follows France into the war against Ottoman! KingdomOfItaly follows France into the war against Ottoman! Switzerland follows France into the war against Ottoman! → display-only
- CMD `declare war on Portugal` → ✓ Choose your war purpose against Portugal.
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on Portugal. Our threat level stands at 100 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, Portugal → proceed
  - POPUP diplomatic_dialogue: proposal_confirm → ally_entry_proceed_without
  - POPUP proposal_result: France declares war on Portugal! Holland follows France into the war against Portugal! KingdomOfItaly follows France into the war against Portugal! Switzerland follows France into the war against Portugal! → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 4 action(s) unused) Turn 3 begins!
- enemy phase: 6 actions, 4 attacks — ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCh… · ArchdukeJohn marches from Tyrol into Carniola unopposed! (232 lost to march) Captured: Bavaria → Austria · ArchdukeCharles holds them at Bohemia while allies attack from Tyrol! (+1 coordination) · [Combat] Brunswick's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Austria: ArchdukeJohn marches from Tyrol into Carniola unopposed! (232 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: ArchdukeCharles holds them at Bohemia while allies attack from Tyrol! (+1 coordination)
  - ⚔ Archduke Charles (lost 2110) vs Deroy (lost 7165) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Archduke Charles (lost 444) vs Deroy (lost 8547) — A grievous defeat for Deroy, Sire. The losses are severe.
  - ⚔ Brunswick (lost 1280) vs Bernadotte (lost 4754) — Bernadotte's army has been badly mauled. Brunswick proved the stronger force today.
  - verbs: attack×4, stance_change×1, wait×1
- LEDGER treasury 4448 · net +2164 · provinces 28 (+0)
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.

## Turn 3 — Late October 1805
- CMD `declare war on Spain` → ✓ Choose your war purpose against Spain.
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on Spain. Our threat level stands at 97 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, Spain → proceed
  - POPUP diplomatic_dialogue: proposal_confirm → ally_entry_proceed_without
- CMD `declare war on Naples` → ✓ Choose your war purpose against Naples.
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on Naples. Our threat level stands at 97 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, Naples → proceed
  - POPUP diplomatic_dialogue: proposal_confirm → ally_entry_proceed_without
  - POPUP proposal_result: France declares war on Naples! Holland follows France into the war against Naples! KingdomOfItaly follows France into the war against Naples! Switzerland follows France into the war against Naples! → display-only
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 action(s) unused) Turn 4 begins!
- enemy phase: 4 actions, 3 attacks — [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack) · [Square broken — Mack breaks formation to attacks] · ArchdukeCharles flanks from Franconia while allies attack from Swabia! (+1 coordination)
  - ⚔ Archduke John (lost 779) vs Bernadotte (lost 73) — Lannes and Massena arrived to reinforce Bernadotte! The timely arrival swung the battle in our favor, Sire.
  - ⚔ Mack (lost 7189) vs Bernadotte (lost 87) — An exemplary engagement by Bernadotte. The outcome was never in doubt.
  - ⚔ Archduke Charles (lost 6722) vs Bernadotte (lost 62) — A decisive victory for Bernadotte! Archduke Charles was thoroughly outmatched.
  - verbs: attack×3, wait×1
- LEDGER treasury 6650 · net +2174 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Bernadotte holds the field at Munich — Archduke Charles's corps is broken and flees.

## Turn 4 — Early November 1805
- CMD `declare war on Papal States` → ✓ Choose your war purpose against PapalStates.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP diplomatic_dialogue: incoming_settlement_offer → reject_settlement_offer
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on PapalStates. Our threat level stands at 97 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, PapalStates → proceed
  - POPUP diplomatic_dialogue: proposal_confirm → ally_entry_proceed_without
  - POPUP proposal_result: France declares war on PapalStates! Holland follows France into the war against PapalStates! KingdomOfItaly follows France into the war against PapalStates! Switzerland follows France into the war against PapalStates! → display-only
- CMD `declare war on Switzerland` → ✓ Choose your war purpose against Switzerland.
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on Switzerland. Our threat level stands at 100 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, Switzerland → proceed
  - POPUP diplomatic_dialogue: proposal_confirm → ally_entry_proceed_without
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 action(s) unused) Turn 5 begins!
- enemy phase: 3 actions, 2 attacks — [Square broken — Mack breaks formation to attacks] · Mack holds them at Munich while allies attack from Swabia! (+1 coordination)
  - 🏴 Austria: [Square broken — Mack breaks formation to attacks]
  - 🏴 Austria: Mack holds them at Munich while allies attack from Swabia! (+1 coordination)
  - ⚔ Mack (lost 657) vs Bernadotte (lost 3165) — Bernadotte stood alone, Sire. Lannes never came.
  - ⚔ Mack (lost 200) vs Deroy (lost 981) — The hills were ours, but Mack took them. Deroy's position was overrun.
  - verbs: attack×2, form_square×1
  - ⚡ AUTONOMOUS: [Combat] Lannes leads the charge! (Aggressive: +15% attack)
  - ⚔ Lannes (lost 208) vs Archduke John (lost 10254) — Massena arrived to reinforce Lannes! The timely arrival swung the battle in our favor, Sire.
  - POPUP capture_choice[capture]: Franconia, Lannes → plunder
- LEDGER treasury 9418 · net +1833 · provinces 29 (+1)
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.

## Turn 5 — Late November 1805
- CMD `declare war on Saxony` → ✓ Choose your war purpose against Saxony.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on Saxony. Our threat level stands at 97 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, Saxony → proceed
  - POPUP diplomatic_dialogue: proposal_confirm → ally_entry_proceed_without
  - POPUP proposal_result: France declares war on Saxony! Holland follows France into the war against Saxony! KingdomOfItaly follows France into the war against Saxony! Switzerland follows France into the war against Saxony! → display-only
- CMD `declare war on Bavaria` → ✓ Choose your war purpose against Bavaria.
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on Bavaria. Our threat level stands at 100 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, Bavaria → proceed
  - POPUP diplomatic_dialogue: proposal_confirm → ally_entry_proceed_without
  - POPUP proposal_result: France declares war on Bavaria! Holland follows France into the war against Bavaria! KingdomOfItaly follows France into the war against Bavaria! Switzerland follows France into the war against Bavaria! → display-only
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 action(s) unused) Turn 6 begins!
- enemy phase: 6 actions, 2 attacks — [Square broken — Mack breaks formation to attacks] · Mack assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). Mack loses 2,777 troops. Garrison holds — 5,000 d…
  - 🏴 Prussia: Brunswick moves from Berlin to Franconia. Franconia falls to Prussia! (was France) (1,395 lost to march)
  - ⚔ Mack (lost 5604) vs Murat (lost 3430) — Murat stood alone, Sire. Ney and Soult never came.
  - verbs: attack×2, form_square×1, stance_change×1, unfortify×1, move×1
  - ⚡ AUTONOMOUS: [Combat] Ney leads the charge! (Aggressive: +15% attack)
  - ⚔ Ney (lost 99) vs Archduke John (lost 1120) — Davout, Lannes, Massena and Napoleon's timely arrival aided Ney. Soult and Murat, however, were conspicuously absent.
  - POPUP capture_choice[capture]: Swabia, Ney → plunder
- LEDGER treasury 11956 · net +1812 · provinces 29 (+0)
- DISPATCH: Sire — Franconia has been taken by Prussia.

## Turn 6 — Early December 1805
- CMD `declare war on Holland` → ✓ Choose your war purpose against Holland.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP diplomatic_dialogue: Prussia, armistice_losing → (left standing)
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on Holland. Our threat level stands at 97 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, Holland → proceed
- CMD `declare war on Hanover` → ✓ Choose your war purpose against Hanover.
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on Hanover. Our threat level stands at 97 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, Hanover → proceed
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 action(s) unused) Turn 7 begins!
  - ⚡ AUTONOMOUS: [Combat] Ney leads the charge! (Aggressive: +15% attack)
  - ⚔ Ney (lost 143) vs Archduke John (lost 778) — Reinforcements from Davout, Lannes, Massena and Napoleon bolstered Ney's position — though Murat never arrived, Sire.
- LEDGER treasury 14005 · net +1875 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Ney holds the field at Munich — Archduke John's corps is broken and flees.

## Turn 7 — Late December 1805
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (20,191; 54,550 if all march) vs Mack (substantial force) at Tyrol — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 84) vs Mack (lost 25241) — Davout, Lannes, Massena and Napoleon's timely arrival bolstered Ney's position. Well-coordinated, Sire.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `Davout, attack Mack` → ✓ Davout firmly objects: 'Sire, the enemy is too strong. We need reinforcements.'
  - POPUP objection: Davout, Davout firmly objects: 'Sire, the enemy is too strong. We need reinforcements.' → trust
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → dismiss
  - POPUP diplomatic_dialogue: Prussia, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 2 action(s) unused) Turn 8 begins!
- LEDGER treasury 15937 · net +1752 · provinces 29 (+0)
- DISPATCH: Sire — Marshal Mack of Austria is taken at Tyrol — he is our prisoner, and their order of battle is one commander shorter.

## Turn 8 — Early January 1806
- CMD `declare war on Hesse` → ✓ Choose your war purpose against Hesse.
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on Hesse. Our threat level stands at 97 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, Hesse → proceed
- CMD `declare war on Sardinia` → ✓ Choose your war purpose against Sardinia.
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on Sardinia. Our threat level stands at 100 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, Sardinia → proceed
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 action(s) unused) Turn 9 begins!
- LEDGER treasury 17717 · net +1591 · provinces 29 (+0)
- DISPATCH: Sire — Ney, Davout, Lannes, Massena and Napoleon stand 84,009 men at Tyrol, which feeds 20,000. 64,009 too many. 11,061 men lost in 2 turns. No depot may be laid at Tyrol — not controlled by France. …

## Turn 9 — Late January 1806
- CMD `Ney, attack Mack` → ✗ Region 'Mack' not found. Did you mean 'La Mancha'?
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `Massena, attack Rome` → ✗ No intelligence on Armfelt's position, Sire. Scout for him before Massena can give chase.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → reject_settlement_offer
  - POPUP diplomatic_dialogue: incoming_proposal → reject_ai_proposal
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 action(s) unused) Turn 10 begins!
- LEDGER treasury 18091 · net +333 · provinces 29 (+0)
- DISPATCH: Sire — Ney, Davout, Lannes, Massena and Napoleon stand 78,971 men at Tyrol, which feeds 20,000. 58,971 too many. 16,099 men lost in 3 turns. No depot may be laid at Tyrol — not controlled by France. …

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP marshal_petition: shadow_command, Marshal Davout asks for a command → detach
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → dismiss
- CMD `economy report` → ✓ ═══════════════════════════════════
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 action(s) unused) Turn 11 begins!
- LEDGER treasury 18932 · net +771 · provinces 28 (-1)
- DISPATCH: Sire — Swabia has been taken by Prussia.

## Turn 11 — Late February 1806
- CMD `Ney, attack Deroy` → ✓ Your words named no foe our maps know, Sire — Ney marches on Archduke John at Carniola, the nearest in sight. Name another and he will turn.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 130) vs Archduke John (lost 9997) — Davout, Lannes, Massena and Napoleon arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire.
  - POPUP capture_choice[capture]: Carniola, Ney → plunder
- CMD `Bernadotte, attack Deroy` → ✗ Marshal Bernadotte is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 3 action(s) unused) Turn 12 begins!
- enemy phase: 1 actions, 1 attacks — [Square broken — Brunswick breaks formation to attacks]
  - ⚔ Brunswick (lost 5127) vs Soult (lost 1689) — Murat arrived to reinforce Soult! The timely arrival swung the battle in our favor, Sire.
  - verbs: attack×1
- LEDGER treasury 19225 · net -123 · provinces 28 (+0)
- DISPATCH: Sire — Rhineland has fallen. Enemy colours fly over French homeland soil.

## Turn 12 — Early March 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
- CMD `economy report` → ✓ ═══════════════════════════════════
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 action(s) unused) Turn 13 begins!
- enemy phase: 3 actions, 3 attacks — Brunswick assaults the Amsterdam garrison! Garrison: 10,000 -> 5,000 (-5,000). Brunswick loses 2,777 troops. Garrison h… · Brunswick assaults the Amsterdam garrison! Garrison collapses (5,000 -> 0). Brunswick loses 1,388 troops in the assault… · Brunswick assaults the Flanders garrison! Garrison: 12,000 -> 6,000 (-6,000). Brunswick loses 3,333 troops. Garrison ho…
  - 🏴 Prussia: Brunswick assaults the Amsterdam garrison! Garrison collapses (5,000 -> 0). Brunswick loses 1,388 troops in the assault. Brunswick marches into Amste…
  - verbs: attack×3
- LEDGER treasury 18051 · net -739 · provinces 28 (+0)
- DISPATCH: Sire — Amsterdam has been taken by Prussia.

## Turn 13 — Late March 1806
- CMD `Soult, hold position` → ✓ Soult will hold Lorraine. [Immovable: +15% defense] "Soult, hold position." It will be done exactly, Sire. (1 AP — Soult executes precise orders with fewer couriers.)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
- CMD `Murat, charge Mack` → ✗ Murat needs to build momentum first! Win battles as attacker to increase recklessness (currently 0).
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 action(s) unused) Turn 14 begins!
- LEDGER treasury 16441 · net -970 · provinces 25 (-3)
- DISPATCH: Sire — Flanders has fallen. Enemy colours fly over French homeland soil.

## Turn 14 — Early April 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP marshal_petition: shadow_command, Marshal Massena asks for a command → detach
  - POPUP diplomatic_dialogue: incoming_settlement_offer → reject_settlement_offer
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → dismiss
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 action(s) unused) Turn 15 begins!
- LEDGER treasury 15039 · net -1040 · provinces 23 (-2)
- DISPATCH: Sire — Normandy has fallen. Enemy colours fly over French homeland soil.

## Turn 15 — Late April 1806
- CMD `Ney, attack Mack` → ✗ Region 'Mack' not found. Did you mean 'La Mancha'?
  - POPUP marshal_petition: shadow_command, Marshal Lannes asks for a command → detach
- CMD `Davout, fortify` → ✓ Davout fortifies position at Carniola. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while forti…
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 3 action(s) unused) Turn 16 begins!
- LEDGER treasury 14420 · net -531 · provinces 23 (+0)
- DISPATCH: Sire — Ney, Davout, Lannes, Massena and Napoleon have been 4 turns over what Carniola can feed. 8,230 men. The country will ask where the army went. A supply depot at Carniola would ease it; Bohemia …

## Turn 16 — Early May 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: Britain, armistice_losing → (left standing)
- CMD `economy report` → ✓ ═══════════════════════════════════
  - POPUP diplomatic_dialogue: Britain, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 action(s) unused) Turn 17 begins!
- LEDGER treasury 13878 · net -463 · provinces 23 (+0)
- DISPATCH: Sire — Ney, Davout, Lannes, Massena and Napoleon have been 5 turns over what Carniola can feed. 7,737 men. The country will ask where the army went. A supply depot at Carniola would ease it; Bohemia …

## Turn 17 — Late May 1806
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 action(s) unused) Turn 18 begins!
- enemy phase: 2 actions, 2 attacks — [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Buxhowden (lost 2401) vs Ney (lost 208) — Complete dominance on the field. Buxhowden crumbled before Ney.
  - ⚔ Buxhowden (lost 10696) vs Lannes (lost 38) — Complete dominance on the field. Buxhowden crumbled before Lannes.
  - verbs: attack×2
- LEDGER treasury 13338 · net -407 · provinces 23 (+0)
- DISPATCH: Sire — Marshal Lannes holds the field at Carniola — Buxhowden's corps is broken and flees.

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  - POPUP diplomatic_dialogue: Naples, armistice_losing → (left standing)
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → dismiss
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 action(s) unused) Turn 19 begins!
- LEDGER treasury 12258 · net -916 · provinces 22 (-1)
- DISPATCH: Sire — Franche-Comte has fallen. Enemy colours fly over French homeland soil.

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 action(s) unused) Turn 20 begins!
- LEDGER treasury 10928 · net -1123 · provinces 21 (-1)
- DISPATCH: Sire — Savoy has fallen. Enemy colours fly over French homeland soil.

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: incoming_settlement_offer → reject_settlement_offer
  - POPUP diplomatic_dialogue: Saxony, armistice_losing → (left standing)
- CMD `economy report` → ✓ ═══════════════════════════════════
  - POPUP diplomatic_dialogue: Saxony, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 action(s) unused) Turn 21 begins!
- enemy phase: 3 actions, 2 attacks — Hohenlohe assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). Hohenlohe loses 2,777 troops. Garrison holds… · Hohenlohe assaults the Milan garrison! Garrison collapses (5,000 -> 0). Hohenlohe loses 1,388 troops in the assault. Ho…
  - 🏴 Prussia: Hohenlohe assaults the Milan garrison! Garrison collapses (5,000 -> 0). Hohenlohe loses 1,388 troops in the assault. Hohenlohe marches into Milan! (1…
  - verbs: attack×2, wait×1
- LEDGER treasury 9554 · net -1156 · provinces 21 (+0)
- DISPATCH: Supply cost you 1,945 men, at Carniola.

## Turn 21 — Late July 1806
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 action(s) unused) Turn 22 begins!
- enemy phase: 2 actions, 1 attacks — [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Buxhowden (lost 2306) vs Napoleon (lost 9) — Complete dominance on the field. Buxhowden crumbled before Napoleon.
  - verbs: attack×1, wait×1
- LEDGER treasury 8382 · net -978 · provinces 21 (+0)
- DISPATCH: Sire — the Emperor Napoleon holds the field at Carniola — Buxhowden's corps is broken and flees.

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 action(s) unused) Turn 23 begins!
- LEDGER treasury 7403 · net -817 · provinces 21 (+0)
- DISPATCH: Davout's fortifications decay: 12% → 11%

## Turn 23 — Late August 1806
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 action(s) unused) Turn 24 begins!
- LEDGER treasury 6592 · net -675 · provinces 21 (+0)
- DISPATCH: Sire — Marshal Ney's household goes unpaid. His patience erodes with his purse.

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: Ottoman, armistice_losing → (left standing)
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → dismiss
- CMD `economy report` → ✓ ═══════════════════════════════════
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 action(s) unused) Turn 25 begins!
- enemy phase: 1 actions, 1 attacks — [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke John (lost 5146) vs Massena (lost 111) — A decisive victory for Massena! Archduke John was thoroughly outmatched.
  - verbs: attack×1
- LEDGER treasury 5905 · net -558 · provinces 21 (+0)
- DISPATCH: Sire — Marshal Massena holds the field at Carniola — Archduke John's corps is broken and flees.

## Turn 25 — Late September 1806
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 action(s) unused) Turn 26 begins!
- enemy phase: 1 actions, 1 attacks — [Combat] Hiller's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Hiller (lost 1687) vs Massena (lost 42) — An exemplary engagement by Massena. The outcome was never in doubt.
  - verbs: attack×1
- LEDGER treasury 5358 · net -450 · provinces 21 (+0)
- DISPATCH: Sire — Marshal Massena holds the field at Carniola — Hiller's corps is broken and flees.

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 action(s) unused) Turn 27 begins!
- LEDGER treasury 4919 · net -365 · provinces 21 (+0)
- DISPATCH: Sire — 4 turns without settlement on Marshal Ney. A rente would close it today; the arrears will not close themselves.

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 action(s) unused) Turn 28 begins!
- LEDGER treasury 4565 · net -294 · provinces 21 (+0)
- DISPATCH: Sire — Marshal Ney's grievance is 5 turns old and has stopped being a household matter. It is now a question of the army.

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `economy report` → ✓ ═══════════════════════════════════
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 action(s) unused) Turn 29 begins!
- enemy phase: 2 actions, 2 attacks — [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Archduke Charles (lost 1227) vs Ney (lost 314) — Stalemate. Ney and Archduke Charles glare at each other across the field.
  - ⚔ Archduke Charles (lost 2153) vs Ney (lost 225) — The engagement proceeded as one might expect, Sire.
  - verbs: attack×2
- LEDGER treasury 4192 · net -201 · provinces 21 (+0)
- DISPATCH: Sire — Marshal Ney's grievance is 6 turns old and has stopped being a household matter. It is now a question of the army.

## Turn 29 — Late November 1806
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 action(s) unused) Turn 30 begins!
- enemy phase: 8 actions, 6 attacks — [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack) · [!] Davout is EXPOSED! (Just retreated, no ally to cover) · ArchdukeCharles holds them at Carniola while allies attack from Bohemia! (+1 coordination)
  - 🏴 Austria: [!] Davout is EXPOSED! (Just retreated, no ally to cover)
  - ⚔ Archduke Charles (lost 977) vs Ney (lost 331) — Stalemate. Ney and Archduke Charles glare at each other across the field.
  - ⚔ Archduke John (lost 342) vs Ney (lost 351) — Even the favorable ground could not save Ney, Sire. Archduke John overcame the terrain.
  - ⚔ Hiller (lost 373) vs Davout (lost 1744) — Davout's fortified position was overwhelmed. A costly investment lost, Sire.
  - ⚔ Archduke Charles (lost 447) vs Lannes (lost 474) — Even the favorable ground could not save Lannes, Sire. Archduke Charles overcame the terrain.
  - ⚔ Hohenlohe (lost 83) vs Napoleon (lost 826) — Napoleon held superior ground, yet Hohenlohe prevailed. A grim day, Sire.
  - ⚔ Yorck (lost 17) vs Napoleon (lost 397) — Napoleon held superior ground, yet Yorck prevailed. A grim day, Sire.
  - verbs: attack×6, grant_pension×2
- LEDGER treasury 3970 · net +148 · provinces 21 (+0)
- DISPATCH: Sire — Marshal Davout has been taken. Austria holds him prisoner.

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → dismiss
  - POPUP diplomatic_dialogue: Prussia, peace → (left standing)
- CMD `economy report` → ✓ ═══════════════════════════════════
  - POPUP diplomatic_dialogue: Prussia, peace → (left standing)
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 action(s) unused) Turn 31 begins!
- enemy phase: 10 actions, 6 attacks — [Combat] Kutuzov's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeJohn's DEFENSIVE stance hampers offensive operations (-10% attack) · Hiller flanks from Tyrol while allies attack from Carniola! (+1 coordination)
  - ⚔ Kutuzov (lost 1036) vs Ney (lost 216) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Archduke Charles (lost 295) vs Lannes (lost 454) — Even the favorable ground could not save Lannes, Sire. Archduke Charles overcame the terrain.
  - ⚔ Archduke John (lost 120) vs Lannes (lost 297) — The hills were ours, but Archduke John took them. Lannes's position was overrun.
  - ⚔ Hiller (lost 39) vs Ney (lost 471) — Ney held superior ground, yet Hiller prevailed. A grim day, Sire.
  - ⚔ Archduke Charles (lost 189) vs Lannes (lost 257) — The hills were ours, but Archduke Charles took them. Lannes's position was overrun.
  - ⚔ Hohenlohe (lost 9) vs Napoleon (lost 105) — Napoleon's army has been badly mauled. Hohenlohe proved the stronger force today.
  - verbs: attack×6, grant_pension×2, fortify×1, grant_dotation×1
- LEDGER treasury 3781 · net +113 · provinces 20 (-1)
- DISPATCH: Sire — Nivernais has fallen. Enemy colours fly over French homeland soil.

---
finished: **completed** · commands 84 · popups 107 · battles 36
