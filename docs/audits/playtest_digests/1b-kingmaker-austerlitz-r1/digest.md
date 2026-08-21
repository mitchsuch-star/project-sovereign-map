# Playtest digest — 1b-kingmaker-austerlitz-r1

seed `austerlitz` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "first", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "dismiss", "petition": "first_enabled", "interrupt": "first", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `vassalize Saxony` → ✗ Cannot create vassal via treaty: requires WAR or OPEN_BORDERS+ (current: PEACE).
- CMD `Massena, move to Piedmont` → ✓ Massena moves from Milan to Piedmont (2,520 lost to march)
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 3 action(s) unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered)
  - ⚔ Archduke Charles (lost 1927) vs Bernadotte (lost 6355) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: move×1, attack×1
- LEDGER treasury 2625 · net +2117 · provinces 28
- DISPATCH: Sire — Bernadotte was mauled at Franconia: 6,355 men lost in a single action.

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `invest in bavaria` → ✗ Bavaria is not a vassal.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Massena, move to Rome` → ✗ Cannot enter Rome — it is controlled by PapalStates (diplomatic state: PEACE). Open borders or higher required.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; 78,676 if all march) vs Mack (large force) at Swabia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 739) vs Mack (lost 14495) — Davout, Lannes and Napoleon arrived to reinforce Ney, but Soult and Murat failed to reach the field in time.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 3 action(s) unused) Turn 3 begins!
- enemy phase: 5 actions, 2 attacks — [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered) · [Shield] Deroy's DEFENSIVE stance strengthens the line! (+15% defense)
  - 🏴 Austria: [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered)
  - ⚔ Archduke Charles (lost 1400) vs Bernadotte (lost 1539) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
  - ⚔ Archduke Charles (lost 1918) vs Deroy (lost 6817) — The hills were ours, but Archduke Charles took them. Deroy's position was overrun.
  - verbs: attack×2, retreat×1, stance_change×1, wait×1
- LEDGER treasury 4708 · net +2197 · provinces 28 (+0)
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `increase autonomy` → ✗ Specify which vassal.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
- CMD `guarantee saxony` → ✓ France guarantees Saxony. Every court that covets their soil now weighs our army in the scale (their willingness falls by 8). Talleyrand: "A guarantee is credibility sta…
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 action(s) unused) Turn 4 begins!
- enemy phase: 3 actions, 2 attacks — ======================================== · [Square broken — ArchdukeCharles breaks formation to attacks]
  - 🏴 Austria: ========================================
  - ⚔ Archduke Charles (lost 226) vs Bernadotte (lost 5573) — Even the favorable ground could not save Bernadotte, Sire. Archduke Charles overcame the terrain.
  - ⚔ Archduke Charles (lost 2154) vs Murat (lost 6180) — Not one corps reached Murat. Soult was expected; Murat fought the battle single-handed.
  - verbs: attack×2, form_square×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 1011) vs Archduke Charles (lost 4511) — Reinforcement from Ney, Davout, Lannes and Napoleon kept Murat standing, Sire — but neither side yielded the ground.
- LEDGER treasury 6657 · net +2407 · provinces 27 (-1)
- DISPATCH: Sire — Rhineland has fallen. Enemy colours fly over French homeland soil.

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `declare war on Papal States` → ✓ Choose your war purpose against PapalStates.
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation → force_declare_war
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on PapalStates. Our threat level stands at 71 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, PapalStates → proceed
  - POPUP diplomatic_dialogue: proposal_confirm → ally_entry_proceed_without
  - POPUP proposal_result: France declares war on PapalStates, shattering the Open Borders Agreement! Holland follows France into the war against PapalStates! KingdomOfItaly follows France into the war against PapalStates! Switzerland follows France into the war against PapalStates! → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 action(s) unused) Turn 5 begins!
- enemy phase: 7 actions, 1 attacks — ArchdukeJohn assaults the Milan garrison! Garrison collapses (7,000 -> 0). ArchdukeJohn loses 1,944 troops in the assau…
  - 🏴 Austria: ArchdukeJohn assaults the Milan garrison! Garrison collapses (7,000 -> 0). ArchdukeJohn loses 1,944 troops in the assault. ArchdukeJohn marches into …
  - verbs: move×2, grant_dotation×2, retreat×1, attack×1, stance_change×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 415) vs Archduke Charles (lost 4755) — Reinforcements from Ney, Davout, Lannes and Napoleon bolstered Murat's position — though Soult never arrived, Sire.
- LEDGER treasury 9251 · net +2418 · provinces 27 (+0)
- DISPATCH: Sire — Milan has been taken by Austria.

## Turn 5 — Late November 1805
- CMD `Massena, attack Rome` → ✓ Massena assaults the Rome garrison! Garrison: 10,000 -> 5,000 (-5,000). Massena loses 2,173 troops. Garrison holds — 5,000 defenders remain.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
- CMD `invest in saxony` → ✗ Saxony is not a vassal.
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 3 action(s) unused) Turn 6 begins!
- enemy phase: 3 actions, 0 attacks
  - verbs: form_square×2, move×1
- LEDGER treasury 11645 · net +2314 · provinces 27 (+0)
- DISPATCH: Sire — Ney, Davout, Lannes, Murat, Bernadotte and Napoleon stand 69,851 men at Franche-Comte, which feeds 52,500. 17,351 too many. 9,016 men lost in 3 turns. No depot may be laid at Franche-Comte — t…

## Turn 6 — Early December 1805
- CMD `Davout, attack Mack` → ✓ Davout notes the risks but prepares the attack. MUSTER — Davout (19,112; 44,169 if all march) vs Mack (32,639 men) at Swabia — the balance of force looks even.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 550) vs Mack (lost 4120) — Reinforcements from Ney, Lannes and Napoleon bolstered Davout's position — though Soult and Murat never arrived, Sire.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
- CMD `cede tyrol to bavaria` → ✗ No province is eligible to cede to Tyrol — it must be conquered land (not your homeland, not a capital, not a marshal's estate) adjoining their territory.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 3 action(s) unused) Turn 7 begins!
- LEDGER treasury 13940 · net +2185 · provinces 27 (+0)
- DISPATCH: Sire — Marshal Davout holds the field at Swabia — Mack's corps is broken and flees.

## Turn 7 — Late December 1805
- CMD `request terms from Papal States` → ✓ PapalStates fights under Britain's lead in France + Spain + Holland + KingdomOfItaly + Switzerland vs Britain + Austria + Russia + PapalStates, Sire — the coalition's te…
  - POPUP marshal_petition: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP diplomatic_dialogue: Austria, armistice_losing → (left standing)
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 action(s) unused) Turn 8 begins!
- enemy phase: 2 actions, 0 attacks
  - verbs: unfortify×1, recruit×1
  - ⚡ AUTONOMOUS: [Combat] Lannes leads the charge! (Aggressive: +15% attack)
  - ⚔ Lannes (lost 236) vs Archduke John (lost 1131) — Ney, Davout and Napoleon's timely arrival bolstered Lannes's position. Well-coordinated, Sire.
- LEDGER treasury 16093 · net +2019 · provinces 27 (+0)
- DISPATCH: Sire — Marshal Lannes holds the field at Franconia — Archduke John's corps is broken and flees.

## Turn 8 — Early January 1806
- CMD `invest in bavaria` → ✗ Berthier peers at the dispatch with concern. "I cannot make sense of this, Sire. A clear order might be: 'Ney, attack Mack' or 'end turn'. For diplomacy: 'declare war on…
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
  - POPUP diplomatic_dialogue: incoming_settlement_offer → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm → seek_bilateral_peace
  - POPUP diplomatic_dialogue: settlement_pair_substitute_confirm, peace → keep_joint_settlement
  - POPUP diplomatic_dialogue: settlement_confirm → seek_bilateral_peace
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (settlement_confirm) answered `seek_bilateral_peace` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `Ney, attack Mack` → ✗ The choice between the joint settlement and a separate peace awaits your answer, Sire — nothing was relayed. Answer with one of: 1=Proceed — peace with Britain alone, 2=…
  - POPUP diplomatic_dialogue: settlement_pair_substitute_confirm, peace → keep_joint_settlement
  - POPUP diplomatic_dialogue: settlement_confirm → seek_bilateral_peace
  - POPUP diplomatic_dialogue: settlement_pair_substitute_confirm, peace → keep_joint_settlement
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (settlement_pair_substitute_confirm, peace) answered `keep_joint_settlement` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `end turn` → ✗ The terms on the table awaits your answer, Sire — nothing was relayed. Answer with one of: 1=Make peace with Britain only, 2=Armistice with Britain only, 3=Open War Deta…
  - POPUP diplomatic_dialogue: settlement_confirm → seek_bilateral_peace
  - POPUP diplomatic_dialogue: settlement_pair_substitute_confirm, peace → keep_joint_settlement
  - POPUP diplomatic_dialogue: settlement_confirm → seek_bilateral_peace
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (settlement_confirm) answered `seek_bilateral_peace` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
- CMD `end turn (retry)` → ✗ The choice between the joint settlement and a separate peace awaits your answer, Sire — nothing was relayed. Answer with one of: 1=Proceed — peace with Britain alone, 2=…
  - POPUP diplomatic_dialogue: settlement_pair_substitute_confirm, peace → keep_joint_settlement
  - POPUP diplomatic_dialogue: settlement_confirm → seek_bilateral_peace
  - POPUP diplomatic_dialogue: settlement_pair_substitute_confirm, peace → keep_joint_settlement
  - ⚠ ANSWER CYCLE — `diplomatic_dialogue` (settlement_pair_substitute_confirm, peace) answered `keep_joint_settlement` 2× in one post; the policy cannot resolve this surface. Stopping the chain.
  - ⚠ end turn still refused after the answer pass — stopping the run

---
finished: **blocked** · commands 27 · popups 37 · battles 10
