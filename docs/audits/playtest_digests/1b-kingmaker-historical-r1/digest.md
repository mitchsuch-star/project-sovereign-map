# Playtest digest — 1b-kingmaker-historical-r1

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "first", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "dismiss", "petition": "first_enabled", "interrupt": "first", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `vassalize Saxony` → ✗ Cannot create vassal via treaty: requires WAR or OPEN_BORDERS+ (current: PEACE).
- CMD `Massena, move to Piedmont` → ✓ Massena moves from Milan to Piedmont (2,520 lost to march)
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 3 action(s) unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered)
  - ⚔ Archduke Charles (lost 2061) vs Bernadotte (lost 6216) — The toll on Bernadotte's forces is heavy, Sire. This defeat will be felt.
  - verbs: move×1, attack×1
- LEDGER treasury 2632 · net +2117 · provinces 28
- DISPATCH: Sire — Bernadotte was mauled at Franconia: 6,216 men lost in a single action.

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `invest in bavaria` → ✗ Bavaria is not a vassal.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Massena, move to Rome` → ✗ Cannot enter Rome — it is controlled by PapalStates (diplomatic state: PEACE). Open borders or higher required.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; 78,676 if all march) vs Mack (large force) at Swabia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 711) vs Mack (lost 15071) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Soult and Murat never arrived, Sire.
  - POPUP diplomatic_dialogue: Prussia, open_borders → (left standing)
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 3 action(s) unused) Turn 3 begins!
- enemy phase: 5 actions, 2 attacks — [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered) · [Shield] Deroy's DEFENSIVE stance strengthens the line! (+15% defense)
  - 🏴 Austria: [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered)
  - ⚔ Archduke Charles (lost 1356) vs Bernadotte (lost 1545) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
  - ⚔ Archduke Charles (lost 2025) vs Deroy (lost 6010) — The hills were ours, but Archduke Charles took them. Deroy's position was overrun.
  - verbs: attack×2, retreat×1, stance_change×1, wait×1
- LEDGER treasury 4720 · net +2197 · provinces 28 (+0)
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `increase autonomy` → ✗ Specify which vassal.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
- CMD `guarantee saxony` → ✓ France guarantees Saxony. Every court that covets their soil now weighs our army in the scale (their willingness falls by 8). Talleyrand: "A guarantee is credibility sta…
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 action(s) unused) Turn 4 begins!
- enemy phase: 4 actions, 2 attacks — ======================================== · [Square broken — ArchdukeCharles breaks formation to attacks]
  - 🏴 Austria: ========================================
  - ⚔ Archduke Charles (lost 639) vs Bernadotte (lost 1691) — Ney marched to Bernadotte's guns as ordered. It was not enough.
  - ⚔ Archduke Charles (lost 1719) vs Murat (lost 7326) — Murat stood alone, Sire. Soult never came.
  - verbs: attack×2, form_square×1, grant_dotation×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 1210) vs Archduke Charles (lost 4818) — Davout, Lannes and Napoleon arrived to reinforce Murat, but Ney failed to reach the field in time.
- LEDGER treasury 6616 · net +2387 · provinces 27 (-1)
- DISPATCH: Sire — Rhineland has fallen. Enemy colours fly over French homeland soil.

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `declare war on Papal States` → ✓ Choose your war purpose against PapalStates.
  - POPUP diplomatic_dialogue: war_purpose_selection → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation → force_declare_war
  - POPUP proposal_result: Sire, I must strongly advise against declaring war on PapalStates. Our threat level stands at 72 — the courts of Europe already whisper of coalition. Another war will only hasten their union against us. → display-only
  - POPUP diplomatic_objection: diplomatic_declare_war, PapalStates → proceed
  - POPUP diplomatic_dialogue: proposal_confirm → ally_entry_proceed_without
  - POPUP proposal_result: France declares war on PapalStates, shattering the Open Borders Agreement! Holland follows France into the war against PapalStates! KingdomOfItaly follows France into the war against PapalStates! Switzerland follows France into the war against PapalStates! → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 action(s) unused) Turn 5 begins!
- enemy phase: 5 actions, 3 attacks — [Shield] Bernadotte stands firm against superior numbers! (Cautious: +10% outnumbered) · ArchdukeJohn assaults the Milan garrison! Garrison collapses (7,000 -> 0). ArchdukeJohn loses 1,944 troops in the assau… · [Alert] ArchdukeCharles's troops are exhausted from repeated attacks! (2nd attack: -10%)
  - 🏴 Austria: ArchdukeJohn assaults the Milan garrison! Garrison collapses (7,000 -> 0). ArchdukeJohn loses 1,944 troops in the assault. ArchdukeJohn marches into …
  - 🏴 Austria: [Alert] ArchdukeCharles's troops are exhausted from repeated attacks! (2nd attack: -10%)
  - ⚔ Archduke Charles (lost 980) vs Bernadotte (lost 977) — Lannes's timely arrival aided Bernadotte. Soult, however, was conspicuously absent.
  - ⚔ Archduke Charles (lost 2181) vs Ney (lost 677) — Reinforcements from Davout and Napoleon bolstered Ney's position — though Soult never arrived, Sire.
  - verbs: attack×3, move×1, grant_dotation×1
- LEDGER treasury 9015 · net +2367 · provinces 26 (-1)
- DISPATCH: Sire — Franche-Comte has fallen. Enemy colours fly over French homeland soil.

## Turn 5 — Late November 1805
- CMD `Massena, attack Rome` → ✓ Massena assaults the Rome garrison! Garrison: 10,000 -> 5,000 (-5,000). Massena loses 2,173 troops. Garrison holds — 5,000 defenders remain.
- CMD `invest in saxony` → ✗ Saxony is not a vassal.
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 3 action(s) unused) Turn 6 begins!
- enemy phase: 4 actions, 0 attacks
  - verbs: form_square×1, fortify×1, move×1, grant_dotation×1
- LEDGER treasury 11143 · net +1993 · provinces 26 (+0)
- DISPATCH: Sire — Marshal Ney's household goes unpaid. His patience erodes with his purse.

## Turn 6 — Early December 1805
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (20,422; 36,272 if all march) vs Mack (substantial force) at Rhineland — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 587) vs Mack (lost 5948) — Lannes, Murat and Napoleon's timely arrival aided Davout. Soult, however, was conspicuously absent.
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
- CMD `cede tyrol to bavaria` → ✗ No province is eligible to cede to Tyrol — it must be conquered land (not your homeland, not a capital, not a marshal's estate) adjoining their territory.
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 3 action(s) unused) Turn 7 begins!
- LEDGER treasury 12777 · net +1518 · provinces 27 (+1)
- DISPATCH: Sire — Marshal Mack of Austria is taken at Rhineland — he is our prisoner, and their order of battle is one commander shorter.

## Turn 7 — Late December 1805
- CMD `request terms from Papal States` → ✓ PapalStates fights under Britain's lead in France + Spain + Holland + KingdomOfItaly + Switzerland vs Britain + Austria + Russia + PapalStates, Sire — the coalition's te…
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 action(s) unused) Turn 8 begins!
- LEDGER treasury 14298 · net +1345 · provinces 27 (+0)
- DISPATCH: Supply cost you 2,549 men, at Piedmont, Rhineland and Lorraine.

## Turn 8 — Early January 1806
- CMD `invest in bavaria` → ✗ Berthier clears his throat. "Forgive me, Sire, but I cannot interpret that order. Our marshals (Ney, Davout, Soult) await clear commands — perhaps 'attack', 'move', 'def…
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
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
finished: **blocked** · commands 27 · popups 34 · battles 10
