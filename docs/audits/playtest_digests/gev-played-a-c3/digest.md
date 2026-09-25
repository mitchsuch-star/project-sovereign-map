# Playtest digest — gev-played-c3

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "proceed", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "client_petition": "grant", "settlement": "decline"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 4 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `7f6e67358f01` (dirty) · content `ccdea5f5afcf` · driver `339f0de8623d`
  - loaded save `save_c2.json` → Loaded: Autosave - Turn 4

## Turn 4 — Early November 1805
  - MAILBOX #4 Hesse counter_offer_response: Hesse — Open Borders Agreement → activated
  - MAILBOX #3 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: Hesse, open_borders #7 → accept
  -     ↳ refused: Sire, another matter has arrived since — this concerns Britain. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_settlement_offer #6 → reject_settlement_offer
  - POPUP diplomatic_dialogue: Hesse, open_borders #7 → accept
  - POPUP proposal_result: You have accepted Hesse's counter-proposal. Treaty signed: Peace → Open Borders with Hesse. → display-only
  - POPUP diplomatic_dialogue: incoming_settlement_offer #6 → reject_settlement_offer
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `vassalize Hesse` → ✓ Hesse has become a Satellite vassal of France (loyalty: 60).
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (16,940; 45,277 if all march, up to 63,206 if every corps arrives) vs Archduke Charles (35,222 men) at Tyrol — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2564, own corps) vs Archduke Charles (lost 2083, own corps) — Massena's timely arrival aided Ney. Davout, Bernadotte and Deroy, however, were conspicuously absent.
- CMD `Napoleon, move to Munich` → ✓ Napoleon moves from Swabia to Munich (170 lost to march)
- CMD `Soult, move to Brabant` → ✓ Soult moves from Lorraine to Brabant (900 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 1 action unused) Turn 5 begins!
- enemy phase: 2 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn's forces advance steadily. Massena holds the line. Casualties: ArchdukeJohn 2,560, Massena 1,436. Both arm… · ArchdukeJohn delivers an effective strike. Bernadotte holds the line. Casualties: ArchdukeJohn 5,264, Bernadotte's army…
  - ⚔ Archduke John (lost 2560) vs Massena (lost 1436) — Where were Ney, Davout and Napoleon? Massena held the field alone — reinforcement never came.
  - ⚔ Archduke John (lost 5264) vs Bernadotte (lost 302, own corps) — Ney failed to arrive in time. Bernadotte's army fought without expected support.
  - verbs: attack×2
  - POPUP marshal_petition: jealousy_confrontation, Marshal Ney seeks an audience → acknowledge
  -     ↳ Ney's grievance runs its course.
- LEDGER treasury 8509 · net +3126 · threat 96 · provinces 28 · ceiling 46816 · army 147408 · vassals Bavaria 72 · Hesse 57 · Holland 98 · Kingdom of Italy 100 · Switzerland 93
  - NET income 3400 · trade 200 · admin 50 · tribute 1543 · upkeep 1346 · charges 531 · blockade 100 · admiralty 90
- DISPATCH: Sire — Marshal Massena holds the field at Milan — Archduke John's corps is driven from Milan yet again — broken, and fleeing.
  - TURN EVENTS 9
- DIPLO +5 medium/low (diplomatic_treaty_signed, diplomatic_carved_vassal_created, diplomatic_we_threshold ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 3 approaches from Austria and Prussia are rebuffed (open borders agreement)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 15 approaches rebuffed, chiefly from Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 6 approaches from Austria and Prussia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)
  - LOG ai_proposal_rejected: We rejected Denmark's open borders agreement proposal
  - LOG ai_proposal_rejected: We rejected Hesse's open borders agreement proposal
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.

---
finished: **completed** · commands 7 · popups 7 · battles 3
