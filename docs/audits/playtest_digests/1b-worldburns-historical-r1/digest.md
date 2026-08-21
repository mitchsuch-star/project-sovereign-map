# Playtest digest — 1b-worldburns-historical-r1

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "decline", "capture": "plunder", "estate": "confiscate", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "dismiss", "petition": "first_enabled", "interrupt": "first", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `declare war on Prussia` → ✓ Choose your war purpose against Prussia.
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on Prussia. Our threat level stands at 70 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, Prussia → proceed
  - POPUP diplomatic_dialogue: proposal_confirm → ally_entry_proceed_without
  - POPUP proposal_result: France declares war on Prussia! Holland follows France into the war against Prussia! KingdomOfItaly follows France into the war against Prussia! Switzerland follows France into the war against Prussia! → display-only
- CMD `declare war on Sweden` → ✓ Choose your war purpose against Sweden.
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on Sweden. Our threat level stands at 90 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
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
  - ⚔ Archduke Charles (lost 5094) vs Massena (lost 5387) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - ⚔ Brunswick (lost 2394) vs Bernadotte (lost 4931) — A narrow defeat for Bernadotte, Sire. Better-prepared troops might have tipped the balance.
  - verbs: attack×2
- LEDGER treasury 2415 · net +2113 · provinces 28
- DISPATCH: Sire — Bernadotte was mauled at Franconia: 4,931 men lost in a single action.

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
- enemy phase: 6 actions, 4 attacks — ArchdukeCharles engages in solid combat. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCharles 2,… · ArchdukeJohn marches from Tyrol into Carniola unopposed! (232 lost to march) Captured: Bavaria → Austria · ArchdukeCharles holds them at Bohemia while allies attack from Tyrol! (+1 coordination) · [Combat] Brunswick's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Austria: ArchdukeJohn marches from Tyrol into Carniola unopposed! (232 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: ArchdukeCharles holds them at Bohemia while allies attack from Tyrol! (+1 coordination)
  - ⚔ Archduke Charles (lost 2527) vs Deroy (lost 5672) — The margin was slim. Training and preparation would serve Deroy well.
  - ⚔ Archduke Charles (lost 826) vs Deroy (lost 7465) — The toll on Deroy's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Brunswick (lost 1265) vs Bernadotte (lost 5526) — The toll on Bernadotte's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×4, stance_change×1, wait×1
- LEDGER treasury 4426 · net +2172 · provinces 28 (+0)
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
  - ⚔ Archduke John (lost 756) vs Bernadotte (lost 73) — Lannes and Massena's timely arrival bolstered Bernadotte's position. Well-coordinated, Sire.
  - ⚔ Mack (lost 5693) vs Bernadotte (lost 93) — A decisive victory for Bernadotte! Mack was thoroughly outmatched.
  - ⚔ Archduke Charles (lost 6623) vs Bernadotte (lost 50) — Complete dominance on the field. Archduke Charles crumbled before Bernadotte.
  - verbs: attack×3, wait×1
- LEDGER treasury 6647 · net +2196 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Bernadotte holds the field at Munich — Archduke Charles's corps is broken and flees.

## Turn 4 — Early November 1805
- CMD `declare war on Papal States` → ✓ Choose your war purpose against PapalStates.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
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
- enemy phase: 4 actions, 0 attacks
  - verbs: stance_change×2, retreat×1, wait×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 254) vs Archduke Charles (lost 13932) — Davout, Massena and Napoleon arrived to reinforce Murat, but Ney, Soult and Lannes failed to reach the field in time.
- LEDGER treasury 9004 · net +2269 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Murat holds the field at Swabia — Archduke Charles's corps is broken and flees.

## Turn 5 — Late November 1805
- CMD `declare war on Saxony` → ✓ Choose your war purpose against Saxony.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
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
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 4 action(s) unused) Turn 6 begins!
  - ⚡ AUTONOMOUS: [Combat] Lannes leads the charge! (Aggressive: +15% attack)
  - ⚔ Lannes (lost 21) vs Archduke John (lost 9113) — Davout, Massena and Napoleon's timely arrival aided Lannes. Murat and Bernadotte, however, were conspicuously absent.
- LEDGER treasury 11401 · net +2254 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Archduke John of Austria is taken at Franconia — he is our prisoner, and their order of battle is one commander shorter.

## Turn 6 — Early December 1805
- CMD `declare war on Holland` → ✓ Choose your war purpose against Holland.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on Holland. Our threat level stands at 97 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, Holland → proceed
  - POPUP diplomatic_dialogue: proposal_confirm → ally_entry_proceed_without
- CMD `declare war on Hanover` → ✓ Choose your war purpose against Hanover.
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on Hanover. Our threat level stands at 97 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, Hanover → proceed
  - POPUP diplomatic_dialogue: proposal_confirm → ally_entry_proceed_without
  - POPUP proposal_result: France declares war on Hanover! Holland follows France into the war against Hanover! KingdomOfItaly follows France into the war against Hanover! Switzerland follows France into the war against Hanover! → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 action(s) unused) Turn 7 begins!
  - ⚡ AUTONOMOUS: [Combat] Massena leads the charge! (Aggressive: +15% attack)
  - ⚔ Massena (lost 166) vs Archduke Charles (lost 7764) — Reinforcements! Davout, Lannes and Napoleon marched onto the field beside Massena. The enemy's advantage melted away.
- LEDGER treasury 13706 · net +2175 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Massena holds the field at Bohemia — Archduke Charles's corps is broken and flees.

## Turn 7 — Late December 1805
- CMD `Ney, attack Mack` → ✓ Ney pursues Mack (at Vienna). Moves to Swabia. Ney: "He is already beaten — he merely has not been told. I will tell him."
  - POPUP marshal_petition: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `Davout, attack Mack` → ✓ Davout notes the risks but prepares the attack. MUSTER — Davout (22,149; 68,162 if all march) vs Mack (large force) at Vienna — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 219) vs Mack (lost 18710) — Lannes, Massena and Napoleon arrived to reinforce Davout! The timely arrival swung the battle in our favor, Sire.
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → dismiss
  - POPUP diplomatic_dialogue: Prussia, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 1 action(s) unused) Turn 8 begins!
- enemy phase: 3 actions, 0 attacks
  - verbs: retreat×1, stance_change×1, grant_dotation×1
- LEDGER treasury 15568 · net +1711 · provinces 29 (+1)
- DISPATCH: Sire — Marshal Davout holds the field at Vienna — Mack's corps is broken and flees.

## Turn 8 — Early January 1806
- CMD `declare war on Hesse` → ✓ Choose your war purpose against Hesse.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on Hesse. Our threat level stands at 97 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, Hesse → proceed
- CMD `declare war on Sardinia` → ✓ Choose your war purpose against Sardinia.
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on Sardinia. Our threat level stands at 100 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, Sardinia → proceed
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 4 action(s) unused) Turn 9 begins!
- enemy phase: 1 actions, 0 attacks
  - verbs: wait×1
  - ⚡ AUTONOMOUS: [Combat] Massena leads the charge! (Aggressive: +15% attack)
  - ⚔ Massena (lost 117) vs Mack (lost 17694) — Reinforcements! Davout, Lannes and Napoleon marched onto the field beside Massena. The enemy's advantage melted away.
  - POPUP capture_choice[capture]: Moravia, Massena → plunder
- LEDGER treasury 17820 · net +1379 · provinces 31 (+2)
- DISPATCH: Sire — Marshal Massena holds the field at Moravia — Mack's corps is broken and flees.

## Turn 9 — Late January 1806
- CMD `Ney, attack Mack` → ✓ Ney: 'ArchdukeCharles bars the way!' Engaging!
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `Massena, attack Rome` → ✗ No intelligence on Armfelt's position, Sire. Scout for him before Massena can give chase.
  - POPUP diplomatic_dialogue: incoming_settlement_offer → reject_settlement_offer
  - POPUP diplomatic_dialogue: incoming_proposal → reject_ai_proposal
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 action(s) unused) Turn 10 begins!
- enemy phase: 8 actions, 2 attacks — [Square broken — Brunswick breaks formation to attacks] · [Combat] Brunswick's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Brunswick (lost 329) vs Bernadotte (lost 2528) — Bernadotte held superior ground, yet Brunswick prevailed. A grim day, Sire.
  - ⚔ Brunswick (lost 2410) vs Ney (lost 5448) — A narrow defeat for Ney, Sire. Better-prepared troops might have tipped the balance.
  - verbs: recruit×2, attack×2, retreat×1, move×1, stance_change×1, wait×1
- LEDGER treasury 17602 · net +247 · provinces 30 (-1)
- DISPATCH: Sire — Bernadotte's corps has been broken at Munich. He must reform before he fights again.

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → dismiss
- CMD `economy report` → ✓ ═══════════════════════════════════
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 action(s) unused) Turn 11 begins!
- enemy phase: 6 actions, 3 attacks — [Square broken — Brunswick breaks formation to attacks] · [Combat] Brunswick's DEFENSIVE stance hampers offensive operations (-10% attack) · Brunswick holds them at Swabia while allies attack from Franconia! (+1 coordination)
  - 🏴 Prussia: Brunswick holds them at Swabia while allies attack from Franconia! (+1 coordination)
  - ⚔ Brunswick (lost 1654) vs Ney (lost 6510) — The toll on Ney's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Brunswick (lost 2439) vs Murat (lost 6232) — Murat stood alone, Sire. Soult never came.
  - ⚔ Brunswick (lost 107) vs Bernadotte (lost 1230) — Where was Soult? Bernadotte held the field alone — reinforcement never came.
  - verbs: attack×3, wait×1, recruit×1, form_square×1
  - POPUP strategic_interrupt: Ney, last_stand, Ney awaits your orders. → fight_to_the_last
- LEDGER treasury 17250 · net +314 · provinces 30 (+0)
- DISPATCH: Sire — Marshal Bernadotte has been taken. Prussia holds him prisoner.

## Turn 11 — Late February 1806
- CMD `Ney, attack Deroy` → ✗ Marshal Ney is a prisoner of Prussia, Sire — no order can reach him until his release.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
- CMD `Bernadotte, attack Deroy` → ✗ Marshal Bernadotte is a prisoner of Prussia, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 4 action(s) unused) Turn 12 begins!
- enemy phase: 5 actions, 2 attacks — Brunswick marches from Swabia into Swabia unopposed! (1,205 lost to march) Captured: France → Prussia · [Square broken — Brunswick breaks formation to attacks]
  - 🏴 Prussia: Brunswick marches from Swabia into Swabia unopposed! (1,205 lost to march) Captured: France → Prussia
  - ⚔ Brunswick (lost 4139) vs Soult (lost 3044) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: attack×2, fortify×1, wait×1, form_square×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 7651) vs Brunswick (lost 1618) — Murat stood alone, Sire. Soult never came.
- LEDGER treasury 17057 · net +293 · provinces 29 (-1)
- DISPATCH: Sire — Marshal Ney has been taken. Prussia holds him prisoner.

## Turn 12 — Early March 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `economy report` → ✓ ═══════════════════════════════════
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 4 action(s) unused) Turn 13 begins!
- enemy phase: 7 actions, 3 attacks — [Square broken — Brunswick breaks formation to attacks] · Brunswick holds them at Lorraine while allies attack from Swabia! (+1 coordination) · Brunswick holds them at Lorraine while allies attack from Swabia! (+1 coordination)
  - ⚔ Brunswick (lost 1805) vs Murat (lost 413) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Brunswick (lost 3159) vs Soult (lost 2802) — Neither Soult nor Brunswick could claim the field. The armies remain locked.
  - ⚔ Brunswick (lost 2293) vs Soult (lost 2499) — Stalemate. Soult and Brunswick glare at each other across the field.
  - verbs: attack×3, grant_dotation×2, wait×1, form_square×1
- LEDGER treasury 16437 · net -205 · provinces 29 (+0)
- DISPATCH: Sire — Murat's corps has been broken at Lorraine. He must reform before he fights again.

## Turn 13 — Late March 1806
- CMD `Soult, hold position` → ✓ Soult will hold Lorraine. [Immovable: +15% defense] "Soult, hold position." It will be done exactly, Sire. (1 AP — Soult executes precise orders with fewer couriers.)
- CMD `Murat, charge Mack` → ✗ Murat needs to build momentum first! Win battles as attacker to increase recklessness (currently 0).
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 action(s) unused) Turn 14 begins!
- enemy phase: 4 actions, 3 attacks — [Combat] Brunswick's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Brunswick's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Brunswick's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Brunswick (lost 2032) vs Soult (lost 2415) — Neither Soult nor Brunswick could claim the field. The armies remain locked.
  - ⚔ Brunswick (lost 1732) vs Soult (lost 2014) — Neither Soult nor Brunswick could claim the field. The armies remain locked.
  - ⚔ Brunswick (lost 1738) vs Soult (lost 1543) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: attack×3, wait×1
- LEDGER treasury 16034 · net -86 · provinces 29 (+0)
- DISPATCH: Sire — Brunswick has crossed into Lorraine. Soult stand in his path.

## Turn 14 — Early April 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: incoming_settlement_offer → reject_settlement_offer
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → dismiss
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 action(s) unused) Turn 15 begins!
- enemy phase: 4 actions, 3 attacks — [Combat] Brunswick's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Brunswick's DEFENSIVE stance hampers offensive operations (-10% attack) · [Square broken — Brunswick breaks formation to attacks]
  - 🏴 Prussia: [Combat] Brunswick's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Brunswick (lost 1229) vs Soult (lost 2493) — Soult was close. A period of drilling could have changed the outcome.
  - ⚔ Brunswick (lost 830) vs Soult (lost 2513) — The line gave way. Soult is falling back, and not in good order.
  - ⚔ Brunswick (lost 233) vs Murat (lost 3440) — The toll on Murat's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×3, form_square×1
- LEDGER treasury 15453 · net -129 · provinces 28 (-1)
- DISPATCH: Sire — Lorraine has fallen. Enemy colours fly over French homeland soil.

## Turn 15 — Late April 1806
- CMD `Ney, attack Mack` → ✗ Marshal Ney is a prisoner of Prussia, Sire — no order can reach him until his release.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Moravia. Defense bonus: +7% (grows +3% per turn, m…
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 action(s) unused) Turn 16 begins!
- enemy phase: 3 actions, 3 attacks — [Combat] Brunswick's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Brunswick's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Brunswick's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Brunswick (lost 119) vs Murat (lost 1800) — Murat's army has been badly mauled. Brunswick proved the stronger force today.
  - ⚔ Brunswick (lost 35) vs Murat (lost 437) — The toll on Murat's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Brunswick (lost 13) vs Murat (lost 193) — Murat's army has been badly mauled. Brunswick proved the stronger force today.
  - verbs: attack×3
- LEDGER treasury 15204 · net -103 · provinces 28 (+0)
- DISPATCH: Sire — Murat was mauled at Orleanais: 1,800 men lost in a single action.

## Turn 16 — Early May 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: Britain, armistice_losing → (left standing)
- CMD `economy report` → ✓ ═══════════════════════════════════
  - POPUP diplomatic_dialogue: Britain, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 4 action(s) unused) Turn 17 begins!
- enemy phase: 4 actions, 4 attacks — [Combat] Brunswick's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Brunswick's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Brunswick's DEFENSIVE stance hampers offensive operations (-10% attack) · Brunswick assaults the Flanders garrison! Garrison: 12,000 -> 8,046 (-3,954). Brunswick loses 4,535 troops. Garrison ho…
  - 🏴 Prussia: [Combat] Brunswick's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Brunswick (lost 8) vs Murat (lost 112) — A grievous defeat for Murat, Sire. The losses are severe.
  - ⚔ Brunswick (lost 2) vs Murat (lost 38) — The toll on Murat's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Brunswick (lost 305) vs Soult (lost 3047) — The toll on Soult's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×4
- LEDGER treasury 15164 · net +259 · provinces 27 (-1)
- DISPATCH: Sire — Orleanais has fallen. Enemy colours fly over French homeland soil.

## Turn 17 — Late May 1806
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 4 action(s) unused) Turn 18 begins!
- enemy phase: 10 actions, 4 attacks — [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Kutuzov's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Mack's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Brunswick's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Britain: Paget moves from Aragon to Bearn. Bearn falls to Britain! (was France) (74 lost to march)
  - 🏴 Prussia: [Combat] Brunswick's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Buxhowden (lost 1682) vs Davout (lost 392) — The prepared defenses proved their worth. Buxhowden could not dislodge Davout.
  - ⚔ Kutuzov (lost 4755) vs Davout (lost 201) — The prepared defenses proved their worth. Kutuzov could not dislodge Davout.
  - ⚔ Mack (lost 5087) vs Davout (lost 226) — A wise investment in fortification. Davout's position was impregnable to Mack's assault.
  - ⚔ Brunswick (lost 168) vs Soult (lost 2344) — The toll on Soult's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×4, move×2, wait×2, retreat×1, stance_change×1
- LEDGER treasury 14814 · net -80 · provinces 24 (-3)
- DISPATCH: Sire — Bearn has fallen. Enemy colours fly over French homeland soil.

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP marshal_petition: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Naples, armistice_losing → (left standing)
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → dismiss
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 action(s) unused) Turn 19 begins!
- enemy phase: 3 actions, 3 attacks — [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Bennigsen's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Buxhowden (lost 1506) vs Davout (lost 1215) — The enemy's repeated assaults have leveled our defenses. We fight without cover.
  - ⚔ Bennigsen (lost 1568) vs Davout (lost 212) — An exemplary engagement by Davout. The outcome was never in doubt.
  - ⚔ Buxhowden (lost 1830) vs Napoleon (lost 227) — An exemplary engagement by Napoleon. The outcome was never in doubt.
  - verbs: attack×3
  - ⚡ AUTONOMOUS: [Combat] Lannes leads the charge! (Aggressive: +15% attack)
  - ⚔ Lannes (lost 161) vs Hiller (lost 2071) — Massena arrived to reinforce Lannes, but Napoleon failed to reach the field in time.
- LEDGER treasury 14114 · net -422 · provinces 23 (-1)
- DISPATCH: Sire — Bordelais has fallen. Enemy colours fly over French homeland soil.

## Turn 19 — Late June 1806
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 action(s) unused) Turn 20 begins!
- enemy phase: 7 actions, 2 attacks — [Combat] Paget's AGGRESSIVE stance drives the assault! (+15% attack) · [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Britain: [Combat] Paget's AGGRESSIVE stance drives the assault! (+15% attack)
  - ⚔ Paget (lost 118) vs Soult (lost 2436) — Soult's army has been badly mauled. Paget proved the stronger force today.
  - ⚔ Buxhowden (lost 3780) vs Davout (lost 226) — Lannes and Massena arrived to reinforce Davout! The timely arrival swung the battle in our favor, Sire.
  - verbs: attack×2, move×2, unfortify×1, wait×1, recruit×1
  - ⚡ AUTONOMOUS: [Combat] Lannes leads the charge! (Aggressive: +15% attack)
  - ⚔ Lannes (lost 2303) vs Mack (lost 3093) — Lannes stood alone, Sire. Massena never came.
- LEDGER treasury 12905 · net -724 · provinces 20 (-3)
- DISPATCH: Sire — Limousin has fallen. Enemy colours fly over French homeland soil.

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: incoming_settlement_offer → reject_settlement_offer
  - POPUP diplomatic_dialogue: Saxony, armistice_losing → (left standing)
- CMD `economy report` → ✓ ═══════════════════════════════════
  - POPUP diplomatic_dialogue: Saxony, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 action(s) unused) Turn 21 begins!
- enemy phase: 2 actions, 2 attacks — Brunswick assaults the Flanders garrison! Garrison collapses (8,046 -> 0). Brunswick loses 2,128 troops in the assault.… · Brunswick assaults the Amsterdam garrison! Garrison: 10,000 -> 5,925 (-4,075). Brunswick loses 2,777 troops. Garrison h…
  - 🏴 Prussia: Brunswick assaults the Flanders garrison! Garrison collapses (8,046 -> 0). Brunswick loses 2,128 troops in the assault. Brunswick marches into Flande…
  - verbs: attack×2
- LEDGER treasury 11800 · net -725 · provinces 16 (-4)
- DISPATCH: Sire — Anjou has fallen. Enemy colours fly over French homeland soil.

## Turn 21 — Late July 1806
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 action(s) unused) Turn 22 begins!
- enemy phase: 5 actions, 3 attacks — Hohenlohe marches from Swabia into Rhineland unopposed! (901 lost to march) Captured: France → Prussia · Hohenlohe marches from Rhineland into Gelderland unopposed! (824 lost to march) Captured: Holland → Prussia · Hohenlohe assaults the Amsterdam garrison! Garrison collapses (7,925 -> 0). Hohenlohe loses 2,201 troops in the assault…
  - 🏴 Prussia: Hohenlohe marches from Swabia into Rhineland unopposed! (901 lost to march) Captured: France → Prussia
  - 🏴 Prussia: Hohenlohe marches from Rhineland into Gelderland unopposed! (824 lost to march) Captured: Holland → Prussia
  - 🏴 Prussia: Hohenlohe assaults the Amsterdam garrison! Garrison collapses (7,925 -> 0). Hohenlohe loses 2,201 troops in the assault. Hohenlohe marches into Amste…
  - verbs: attack×3, move×1, defend×1
- LEDGER treasury 10667 · net -909 · provinces 15 (-1)
- DISPATCH: Sire — Rhineland has fallen. Enemy colours fly over French homeland soil.

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 4 action(s) unused) Turn 23 begins!
- enemy phase: 1 actions, 1 attacks — [Combat] Mack's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Mack (lost 4320) vs Davout (lost 129) — A wise investment in fortification. Davout's position was impregnable to Mack's assault.
  - verbs: attack×1
- LEDGER treasury 9705 · net -754 · provinces 15 (+0)
- DISPATCH: Sire — Brabant has been taken by Prussia.

## Turn 23 — Late August 1806
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 action(s) unused) Turn 24 begins!
- enemy phase: 9 actions, 7 attacks — [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack) · [Shield] Massena steps forward to cover Davout's retreat! "Davout is in no condition to fight - I'll handle this!" · [Shield] Massena steps forward to cover Lannes's retreat! "Lannes is in no condition to fight - I'll handle this!"
  - 🏴 Austria: [Combat] ArchdukeCharles's DEFENSIVE stance hampers offensive operations (-10% attack)
  - 🏴 Prussia: Hohenlohe marches from Lorraine into Franche-Comte unopposed! (465 lost to march) Captured: France → Prussia
  - 🏴 Prussia: Hohenlohe assaults the Bern garrison! Garrison collapses (5,000 -> 0). Hohenlohe loses 1,736 troops in the assault. Hohenlohe marches into Bern! (376…
  - ⚔ Buxhowden (lost 3996) vs Lannes (lost 172) — An exemplary engagement by Lannes. The outcome was never in doubt.
  - ⚔ Archduke Charles (lost 809) vs Davout (lost 1456) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
  - ⚔ Archduke Charles (lost 952) vs Massena (lost 2598) — Even the favorable ground could not save Massena, Sire. Archduke Charles overcame the terrain.
  - ⚔ Archduke Charles (lost 563) vs Massena (lost 4486) — Even the favorable ground could not save Massena, Sire. Archduke Charles overcame the terrain.
  - verbs: attack×7, move×1, grant_pension×1
  - ⚡ AUTONOMOUS: [Combat] Lannes leads the charge! (Aggressive: +15% attack)
  - ⚔ Lannes (lost 112) vs Bennigsen (lost 2057) — Reinforcements! Massena and Napoleon marched onto the field beside Lannes. The enemy's advantage melted away.
  - POPUP capture_choice[capture]: Ukraine, Lannes → plunder
- LEDGER treasury 8441 · net -1108 · provinces 14 (-1)
- DISPATCH: Sire — Franche-Comte has fallen. Enemy colours fly over French homeland soil.

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP marshal_petition: shadow_command, Marshal Massena asks for a command → detach
  - POPUP diplomatic_dialogue: Ottoman, armistice_losing → (left standing)
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → dismiss
- CMD `economy report` → ✓ ═══════════════════════════════════
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 action(s) unused) Turn 25 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: retreat×1, stance_change×1
- LEDGER treasury 6483 · net -1464 · provinces 8 (-6)
- DISPATCH: Sire — Languedoc has fallen. Enemy colours fly over French homeland soil.

## Turn 25 — Late September 1806
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 action(s) unused) Turn 26 begins!
- enemy phase: 8 actions, 6 attacks — [Combat] Kutuzov's DEFENSIVE stance hampers offensive operations (-10% attack) · Kutuzov holds them at Ukraine while allies attack from Lithuania! (+1 coordination) · Kutuzov holds them at Ukraine while allies attack from Lithuania! (+1 coordination) · Kutuzov holds them at Ukraine while allies attack from Lithuania! (+1 coordination)
  - 🏴 Prussia: Hohenlohe assaults the Milan garrison! Garrison collapses (5,000 -> 0). Hohenlohe loses 1,388 troops in the assault. Hohenlohe marches into Milan! (1…
  - ⚔ Kutuzov (lost 955) vs Davout (lost 899) — Napoleon reached Davout in time, Sire — but even together, the field could not be held.
  - ⚔ Kutuzov (lost 612) vs Lannes (lost 899) — Even the favorable ground could not save Lannes, Sire. Kutuzov overcame the terrain.
  - ⚔ Kutuzov (lost 499) vs Lannes (lost 730) — Even the favorable ground could not save Lannes, Sire. Kutuzov overcame the terrain.
  - ⚔ Kutuzov (lost 385) vs Lannes (lost 464) — The hills were ours, but Kutuzov took them. Lannes's position was overrun.
  - verbs: attack×6, unfortify×1, grant_pension×1
- LEDGER treasury 4514 · net -1223 · provinces 6 (-2)
- DISPATCH: Sire — Champagne has fallen. Enemy colours fly over French homeland soil.

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 action(s) unused) Turn 27 begins!
- enemy phase: 4 actions, 3 attacks — [Combat] Kutuzov's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Kutuzov's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Mack's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Kutuzov (lost 280) vs Lannes (lost 486) — Even the favorable ground could not save Lannes, Sire. Kutuzov overcame the terrain.
  - ⚔ Kutuzov (lost 220) vs Lannes (lost 368) — The hills were ours, but Kutuzov took them. Lannes's position was overrun.
  - ⚔ Mack (lost 537) vs Lannes (lost 317) — Stalemate. Lannes and Mack glare at each other across the field.
  - verbs: attack×3, grant_pension×1
- LEDGER treasury 3165 · net -909 · provinces 5 (-1)
- DISPATCH: Sire — Ardennes has fallen. Enemy colours fly over French homeland soil.

## Turn 27 — Late October 1806
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 action(s) unused) Turn 28 begins!
- enemy phase: 2 actions, 2 attacks — [Combat] Kutuzov's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Kutuzov's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Kutuzov (lost 219) vs Lannes (lost 204) — Napoleon marched to Lannes's guns as ordered. It was not enough.
  - ⚔ Kutuzov (lost 134) vs Lannes (lost 247) — The hills were ours, but Kutuzov took them. Lannes's position was overrun.
  - verbs: attack×2
- LEDGER treasury 2219 · net -663 · provinces 5 (+0)
- DISPATCH: Sire — Lannes, crowned three turns ago, has been hunted across the frontier by Kutuzov.

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `economy report` → ✓ ═══════════════════════════════════
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 action(s) unused) Turn 29 begins!
- enemy phase: 5 actions, 4 attacks — [Combat] Kutuzov's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack) · Buxhowden holds them at Podolia while allies attack from Lithuania! (+1 coordination) · [!] Napoleon is EXPOSED! (Just retreated, no ally to cover)
  - 🏴 Russia: [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Kutuzov (lost 103) vs Lannes (lost 189) — The hills were ours, but Kutuzov took them. Lannes's position was overrun.
  - ⚔ Buxhowden (lost 878) vs Davout (lost 2286) — Even Davout's fortifications could not hold, Sire. Buxhowden overran the position.
  - ⚔ Buxhowden (lost 76) vs Napoleon (lost 329) — The toll on Napoleon's forces is heavy, Sire. This defeat will be felt.
  - ⚔ Archduke Charles (lost 6) vs Napoleon (lost 157) — Napoleon's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×4, grant_pension×1
- LEDGER treasury 1702 · net -344 · provinces 4 (-1)
- DISPATCH: Sire — Nivernais has fallen. Enemy colours fly over French homeland soil.

## Turn 29 — Late November 1806
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 action(s) unused) Turn 30 begins!
- enemy phase: 7 actions, 5 attacks — [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack) · Bennigsen holds them at Ukraine while allies attack from Podolia! (+1 coordination) · Kutuzov holds them at Ukraine while allies attack from Podolia! (+1 coordination) · Bennigsen holds them at Ukraine while allies attack from Podolia! (+1 coordination)
  - ⚔ Buxhowden (lost 67) vs Lannes (lost 162) — Even the favorable ground could not save Lannes, Sire. Buxhowden overcame the terrain.
  - ⚔ Bennigsen (lost 1) vs Lannes (lost 146) — Lannes held superior ground, yet Bennigsen prevailed. A grim day, Sire.
  - ⚔ Kutuzov (lost 20) vs Lannes (lost 101) — Even the favorable ground could not save Lannes, Sire. Kutuzov overcame the terrain.
  - ⚔ Bennigsen (lost 0) vs Lannes (lost 86) — Lannes held superior ground, yet Bennigsen prevailed. A grim day, Sire.
  - ⚔ Mack (lost 10) vs Napoleon (lost 50) — Napoleon's army has been badly mauled. Mack proved the stronger force today.
  - verbs: attack×5, grant_pension×2
- LEDGER treasury 1310 · net -336 · provinces 4 (+0)
- DISPATCH: Sire — Lannes, crowned five turns ago, has been hunted on consecutive turns by Kutuzov.

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Talleyrand, assess our situation` → ✓ Sire — the state of Europe, plainly told.
  - POPUP diplomatic_dialogue: advisory → dismiss
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `economy report` → ✓ ═══════════════════════════════════
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 action(s) unused) Turn 31 begins!
- enemy phase: 5 actions, 4 attacks — [Combat] Bennigsen's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Buxhowden's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Kutuzov's DEFENSIVE stance hampers offensive operations (-10% attack) · [Combat] Bennigsen's DEFENSIVE stance hampers offensive operations (-10% attack)
  - ⚔ Bennigsen (lost 0) vs Lannes (lost 56) — The hills were ours, but Bennigsen took them. Lannes's position was overrun.
  - ⚔ Buxhowden (lost 20) vs Lannes (lost 56) — The hills were ours, but Buxhowden took them. Lannes's position was overrun.
  - ⚔ Kutuzov (lost 7) vs Lannes (lost 35) — Lannes held superior ground, yet Kutuzov prevailed. A grim day, Sire.
  - ⚔ Bennigsen (lost 0) vs Lannes (lost 30) — Even the favorable ground could not save Lannes, Sire. Bennigsen overcame the terrain.
  - verbs: attack×4, grant_pension×1
- LEDGER treasury 955 · net -336 · provinces 4 (+0)
- DISPATCH: Sire — Lannes was mauled at Ukraine: 130 men lost in a single action.

---
finished: **completed** · commands 84 · popups 107 · battles 74
