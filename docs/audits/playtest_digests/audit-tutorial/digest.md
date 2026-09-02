# Playtest digest — audit-tutorial

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "decline", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "dismiss", "petition": "first_enabled", "interrupt": "first", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `economy` → ✓ ═══════════════════════════════════
- CMD `Senarmont, move to Munich` → ✓ There is no Marshal 'Senarmont' in the order of battle, Sire. Whom did you intend?
  - POPUP clarification: Berthier, unknown_name, There is no Marshal 'Senarmont' in the order of battle, Sire. Whom did you intend? → 1 (first option: Bernadotte)
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 3 action(s) unused) Turn 2 begins!
- enemy phase: 3 actions, 1 attacks — [Shield] Massena is at his best with his back to the wall! (Child of Victory: +10% defense when outnumbered)
  - ⚔ Archduke Charles (lost 4036) vs Massena (lost 6497) — Not one corps reached Massena. Bernadotte was expected; Massena fought the battle single-handed.
  - verbs: move×1, stance_change×1, attack×1
- LEDGER treasury 2333 · net +1844 · provinces 28
- DISPATCH: Sire — Swabia has been taken by Austria.

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → decline
  - LETTER Portugal: Open Borders Agreement → decline
- CMD `Ney, defend` → ✓ Ney firmly objects: 'I would rather attack than sit idle.'
  - POPUP objection: Ney, Ney firmly objects: 'I would rather attack than sit idle.' → trust
  - POPUP diplomatic_dialogue: Prussia, open_borders #2 → reject
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1286) vs Mack (lost 10831) — Davout and Napoleon's timely arrival aided Ney. Soult, Lannes, Murat and Bernadotte, however, were conspicuously absent.
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 3 action(s) unused) Turn 3 begins!
- enemy phase: 4 actions, 4 attacks — [Shield] Massena is at his best with his back to the wall! (Child of Victory: +10% defense when outnumbered) · ======================================== · [Shield] Massena is at his best with his back to the wall! (Child of Victory: +10% defense when outnumbered) · [Shield] Massena is at his best with his back to the wall! (Child of Victory: +10% defense when outnumbered)
  - 🏴 Austria: ========================================
  - 🏴 Austria: [Shield] Massena is at his best with his back to the wall! (Child of Victory: +10% defense when outnumbered)
  - ⚔ Archduke Charles (lost 3541) vs Massena (lost 5720) — Massena stood alone, Sire. Bernadotte never came.
  - ⚔ Archduke John (lost 6518) vs Bernadotte (lost 166) — Ney and Lannes's timely arrival bolstered Bernadotte's position. Well-coordinated, Sire.
  - ⚔ Archduke Charles (lost 2482) vs Massena (lost 5093) — Massena stood alone, Sire. Bernadotte never came.
  - ⚔ Archduke Charles (lost 1734) vs Massena (lost 5431) — Where was Bernadotte? Massena held the field alone — reinforcement never came.
  - verbs: attack×4
- LEDGER treasury 3964 · net +2511 · provinces 28 (+0)
- DISPATCH: Sire — Massena's corps has been broken at Milan. He must reform before he fights again.

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → decline
  - LETTER Saxony: Open Borders Agreement → decline
- CMD `Ney, attack Kienmayer` → ✓ Your words named no foe our maps know, Sire — Ney marches on Mack at Franconia, the nearest in sight. Name another and he will turn.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 196) vs Mack (lost 29072) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Bernadotte never arrived, Sire.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 3 action(s) unused) Turn 4 begins!
- enemy phase: 4 actions, 3 attacks — [Shield] Massena is at his best with his back to the wall! (Child of Victory: +10% defense when outnumbered) · [Square broken — ArchdukeCharles breaks formation to attacks] · [Alert] ArchdukeCharles's troops are exhausted from repeated attacks! (3rd attack: -20%)
  - ⚔ Archduke Charles (lost 5074) vs Massena (lost 396) — Ney and Murat arrived to reinforce Massena! The timely arrival swung the battle in our favor, Sire.
  - ⚔ Archduke Charles (lost 5113) vs Ney (lost 499) — Complete dominance on the field. Archduke Charles crumbled before Ney.
  - ⚔ Archduke Charles (lost 9467) vs Ney (lost 185) — A decisive victory for Ney! Archduke Charles was thoroughly outmatched.
  - verbs: attack×3, form_square×1
- LEDGER treasury 6484 · net +2552 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Ney holds the field at Franconia — Mack's corps is broken and flees.

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → decline
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `Senarmont, bombard Jellacic` → ✓ There is no Marshal 'Senarmont' in the order of battle, Sire. Whom did you intend?
  - POPUP clarification: Berthier, unknown_name, There is no Marshal 'Senarmont' in the order of battle, Sire. Whom did you intend? → 1 (first option: Bernadotte)
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: incoming_settlement_offer #9 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 4 action(s) unused) Turn 5 begins!
- enemy phase: 3 actions, 0 attacks
  - verbs: retreat×1, stance_change×1, wait×1
  - ⚡ AUTONOMOUS: [Combat] Lannes leads the charge! (Aggressive: +15% attack)
  - ⚔ Lannes (lost 41) vs Mack (lost 7550) — Davout and Napoleon's timely arrival aided Lannes. Ney, Murat and Bernadotte, however, were conspicuously absent.
- LEDGER treasury 9225 · net +2556 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Lannes holds the field at Tyrol — Mack's corps breaks a second time on this ground and flees.

## Turn 5 — Late November 1805
- CMD `Davout, march to Franconia` → ✓ Davout begins march to Franconia. Moves to Franconia. Davout: "We move deliberately — arrival is worth little if the army arrives broken."
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Austria, armistice_losing #11 → reject
  - POPUP proposal_result: You have rejected Austria's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 2 action(s) unused) Turn 6 begins!
- enemy phase: 3 actions, 1 attacks — [!] ArchdukeCharles is EXPOSED! (Just retreated, no ally to cover)
  - 🏴 Bavaria: [!] ArchdukeCharles is EXPOSED! (Just retreated, no ally to cover)
  - ⚔ Deroy (lost 921) vs Archduke Charles (lost 3755) — Even the favorable ground could not save Archduke Charles, Sire. Deroy overcame the terrain.
  - verbs: move×2, attack×1
  - ⚡ AUTONOMOUS: [Combat] Lannes leads the charge! (Aggressive: +15% attack)
  - ⚔ Lannes (lost 6) vs Mack (lost 1695) — Ney, Massena and Napoleon's timely arrival aided Lannes. Murat and Bernadotte, however, were conspicuously absent.
- LEDGER treasury 11855 · net +2439 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Lannes holds the field at Milan — Mack's corps is driven from Milan yet again — broken, and fleeing.

## Turn 6 — Early December 1805
  - LETTER Ottoman: Open Borders Agreement → decline
- CMD `Ney, attack Jellacic` → ✓ Your words named no foe our maps know, Sire — Ney marches on Mack at Piedmont, the nearest in sight. Name another and he will turn.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 3) vs Mack (lost 277) — Lannes, Massena and Napoleon arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Prussia, open_borders #12 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 3 action(s) unused) Turn 7 begins!
- LEDGER treasury 14222 · net +2187 · provinces 28 (+0)
- DISPATCH: Sire — Marshal Mack of Austria is destroyed at Piedmont — his corps annihilated, his name struck from their order of battle.

## Turn 7 — Late December 1805
  - LETTER Portugal: Open Borders Agreement → decline
  - LETTER Denmark: Open Borders Agreement → decline
- CMD `Soult, recruit troops` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 640 gold. Morale: 100% -> 94%
- CMD `build watchtower in Lorraine` → ✓ Construction started: Watchtower in Lorraine (2 turns, 250 gold)
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 4 action(s) unused) Turn 8 begins!
- enemy phase: 3 actions, 1 attacks — Deroy marches from Bohemia into Carniola unopposed! (189 lost to march) Captured: Austria → Bavaria
  - 🏴 Bavaria: Deroy marches from Bohemia into Carniola unopposed! (189 lost to march) Captured: Austria → Bavaria
  - verbs: attack×1, move×1, wait×1
- LEDGER treasury 15499 · net +2045 · provinces 28 (+0)
- DISPATCH: Sire — Asturias has been taken by Britain.

## Turn 8 — Early January 1806
  - LETTER Saxony: Open Borders Agreement → decline
  - LETTER Hesse: Non-Aggression Pact → decline
- CMD `Davout, scout Bohemia` → ✓ Davout scouts Bohemia: Controlled by Bavaria. Terrain: Plains. No enemy forces detected.
  - POPUP marshal_petition: fontainebleau, The marshals petition the Emperor → concede
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 3 action(s) unused) Turn 9 begins!
- enemy phase: 7 actions, 4 attacks — ArchdukeCharles marches from Vienna into Bohemia unopposed! (139 lost to march) Captured: Bavaria → Austria · ArchdukeCharles marches from Bohemia into Carniola unopposed! (165 lost to march) Captured: Bavaria → Austria · Deroy marches from Tyrol into Carniola unopposed! (185 lost to march) Captured: Austria → Bavaria · [Shield] ArchdukeCharles's DEFENSIVE stance strengthens the line! (+15% defense)
  - 🏴 Austria: ArchdukeCharles marches from Vienna into Bohemia unopposed! (139 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: ArchdukeCharles marches from Bohemia into Carniola unopposed! (165 lost to march) Captured: Bavaria → Austria
  - 🏴 Bavaria: Deroy marches from Tyrol into Carniola unopposed! (185 lost to march) Captured: Austria → Bavaria
  - 🏴 Bavaria: Deroy moves from Carniola to Bohemia. Bohemia falls to Bavaria! (was Austria) (152 lost to march)
  - ⚔ Deroy (lost 1486) vs Archduke Charles (lost 1210) — Neither Archduke Charles nor Deroy could claim the field. The armies remain locked.
  - verbs: attack×4, move×3
- LEDGER treasury 16338 · net +770 · provinces 28 (+0)
- DISPATCH: Sire — Bohemia has been taken by Austria.

## Turn 9 — Late January 1806
  - LETTER PapalStates: Open Borders Agreement → decline
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Pie…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #19 → reject_settlement_offer
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 2 action(s) unused) Turn 10 begins!
- LEDGER treasury 17081 · net +680 · provinces 28 (+0)
- DISPATCH: Sire — 3 turns of famine at Piedmont now. 6,250 men gone, and not one of them to the enemy. Kingdom of Italy's magazines feed us as our own — the army is simply too large for the province. Provence c…

## Turn 10 — Early February 1806
  - LETTER Ottoman: Open Borders Agreement → decline
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP marshal_petition: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  - POPUP diplomatic_dialogue: Prussia, open_borders #20 → reject
  - POPUP proposal_result: You have rejected Prussia's proposal. Talleyrand will convey your decision. → display-only
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 4 action(s) unused) Turn 11 begins!
- enemy phase: 7 actions, 2 attacks — [Square broken — Castanos breaks formation to attacks] · [Square broken — Castanos breaks formation to attacks]
  - 🏴 Austria: ArchdukeCharles moves from Vienna to Bohemia. Bohemia falls to Austria! (was Bavaria) (484 lost to march — forward supply lines reduce losses)
  - ⚔ Castanos (lost 790) vs Paget (lost 1026) — Stalemate. Paget and Castanos glare at each other across the field.
  - ⚔ Castanos (lost 528) vs Paget (lost 1042) — The margin was slim. Training and preparation would serve Paget well.
  - verbs: move×2, attack×2, unfortify×1, wait×1, form_square×1
- LEDGER treasury 17747 · net +607 · provinces 28 (+0)
- DISPATCH: Sire — Bohemia has been taken by Austria.

---
finished: **completed** · commands 22 · popups 35 · battles 17
