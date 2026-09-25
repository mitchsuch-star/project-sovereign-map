# Playtest digest — vpr1-played-a-c3

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "proceed", "interrupt": "first", "last_stand": "breakout", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "settlement": "decline", "decline_from": "Hanover,Austria"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 4 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `08ed3d374c35` (dirty) · content `ac2f6d51ede2` · driver `196c4ee545c1`
  - loaded save `A2_save_2.json` → Loaded: Autosave - Turn 4

## Turn 4 — Early November 1805
  - MAILBOX #3 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #5 → reject_settlement_offer
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- CMD `vassalize Hesse` → ✓ Hesse has become a Satellite vassal of France (loyalty: 60).
- CMD `Davout, unfortify` → ✗ Davout is not currently fortified.
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (11,224; expect about 40,592 with the corps likely to arrive, up to 41,934 if all march) vs Archduke Charles (27,649 men) at Tyrol — the balance of force lo…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1459, own corps) vs Archduke Charles (lost 1679, own corps) — Lannes and Massena's timely arrival aided Ney. Deroy, however, was conspicuously absent.
- CMD `Napoleon, move to Munich` → ✓ Napoleon moves from Swabia to Munich (154 lost to march)
- CMD `Soult, move to Brabant` → ✓ Soult moves from Lorraine to Brabant (900 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 1 action unused) Turn 5 begins!
- enemy phase: 5 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn's forces advance steadily. Massena holds the line. Casualties: ArchdukeJohn 2,415, Massena 1,413. Both arm… · ArchdukeJohn delivers an effective strike. Napoleon holds the line. Casualties: ArchdukeJohn 1,464, Napoleon 595. Both …
  - ⚔ Archduke John (lost 2415) vs Massena (lost 1413) — Where was Napoleon? Massena held the field alone — reinforcement never came.
  - ⚔ Archduke John (lost 1464) vs Napoleon (lost 595) — Where was Deroy? Napoleon held the field alone — reinforcement never came.
  - verbs: attack×2, unfortify×1, wait×1, recruit×1
- ENVOYS WAITING 1 · Denmark non aggression
- LEDGER treasury 9054 · net +3290 · threat 96 · provinces 28 · ceiling 43182 · army 132184 · vassals Bavaria 70 · Hesse 57 · Holland 96 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 275 · admin 50 · tribute 1497 · upkeep 1024 · charges 680 · blockade 138 · admiralty 90
- DISPATCH: Sire — Ney's corps has been broken at Munich. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - TURN EVENTS 8
- DIPLO +3 medium/low (diplomatic_carved_vassal_created, diplomatic_we_threshold, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 6 approaches from Austria and Prussia are rebuffed (open borders agreement)
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
finished: **completed** · commands 7 · popups 3 · battles 3
