# Playtest digest — vpr1-played-a-c2

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "proceed", "interrupt": "first", "last_stand": "breakout", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "settlement": "decline", "decline_from": "Hanover,Austria"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 3 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `08ed3d374c35` (dirty) · content `ac2f6d51ede2` · driver `196c4ee545c1`
  - loaded save `A2_save_1.json` → Loaded: Autosave - Turn 3

## Turn 3 — Late October 1805
- CMD `propose open borders with Hesse` → ✗ We already have Open Borders with Hesse. Talleyrand sees no purpose in proposing what we already possess.
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (19,054; expect about 73,764 with the corps likely to arrive, up to 104,462 if all march) vs Archduke Charles (large force) at Tyrol — the balance of force …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2665, own corps) vs Archduke Charles (lost 4624, own corps) — Lannes and Massena's timely arrival aided Ney. Davout, Murat, Bernadotte and Deroy, however, were conspicuously absent.
- CMD `Murat, attack Archduke Charles` → ✓ MUSTER — Murat (20,393) vs Archduke Charles (42,873 men) at Tyrol — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 10116) vs Archduke Charles (lost 1161, own corps) — Murat stood alone, Sire. Ney, Davout and Deroy never came.
- CMD `Lannes, attack Archduke Charles` → ✓ MUSTER — Lannes (12,493; expect about 36,829 with the corps likely to arrive, up to 50,580 if all march) vs Archduke Charles (41,712 men) at Tyrol — the balance of force…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 2069, own corps) vs Archduke Charles (lost 2932, own corps) — Reinforcements from Ney and Davout bolstered Lannes's position — though Bernadotte and Deroy never arrived, Sire.
- CMD `Davout, attack Archduke Charles` → ✓ Davout firmly objects: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will fortify current position instead.)
  - POPUP objection: Davout, Davout firmly objects: 'The odds are not in our favor. Perhaps we should reconsider.' (Trust him and he will fortify current position instead.) → insist
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 6236) vs Archduke Charles (lost 956, own corps) — Davout stood alone, Sire. Deroy never came.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 3 ended. Turn 4 begins!
- enemy phase: 6 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · ArchdukeCharles attacks with overwhelming force. Brutal stalemate between ArchdukeCharles and Ney. Heavy casualties on … · ArchdukeCharles's forces press forward aggressively. Brutal stalemate between ArchdukeCharles and Lannes. Heavy casualt…
  - ⚔ Archduke Charles (lost 3351) vs Massena (lost 4032) — An inconclusive affair. Both sides bloodied but unbroken.
  - ⚔ Archduke Charles (lost 3132) vs Ney (lost 1413, own corps) — Reinforcements from Napoleon bolstered Ney's position — though Bernadotte and Deroy never arrived, Sire.
  - ⚔ Archduke Charles (lost 3241) vs Lannes (lost 791, own corps) — Bernadotte arrived to reinforce Lannes, but Deroy failed to reach the field in time.
  - verbs: attack×3, break_square×1, stance_change×1, fortify×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: incoming_settlement_offer #5 → reject_settlement_offer
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 5811 · net +3256 · threat 93 · provinces 28 · ceiling 43493 · army 142948 · vassals Bavaria 66 · Holland 95 · Kingdom of Italy 97 · Switzerland 92
  - NET income 3400 · trade 325 · admin 50 · tribute 1267 · upkeep 1204 · charges 329 · blockade 163 · admiralty 90
- DISPATCH: Sire — Murat's corps has been broken at Munich. He must reform before he fights again.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Offering 1358 gold.
  - TURN EVENTS 5
- DIPLO +4 medium/low (diplomatic_we_threshold ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Denmark rebuffs Prussia (open borders agreement)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 11 approaches from Prussia, Naples and Denmark are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: 6 approaches from Austria and Prussia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.

---
finished: **completed** · commands 7 · popups 7 · battles 7
