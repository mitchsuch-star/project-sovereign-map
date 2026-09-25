# Playtest digest — gev-played-cB5

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "proceed", "interrupt": "first", "last_stand": "breakout", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "client_petition": "grant", "settlement": "decline"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 9 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `7f6e67358f01` (dirty) · content `ccdea5f5afcf` · driver `196c4ee545c1`
  - loaded save `save_cB4.json` → Loaded: Autosave - Turn 9
  - POPUP strategic_interrupt: Ney, last_stand, Ney is cornered at Bohemia with 3,840 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → attempt_breakout

## Turn 9 — Late January 1806
  - MAILBOX #11 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #13 → reject_settlement_offer
- CMD `invest in Saxony` → ✓ Invested in Saxony: +10 loyalty (35 → 45). Cost: 1 DP + 200g. Cooldown: 3 turns.
- CMD `Massena, attack Milan` → ✓ Massena assaults the Milan garrison! Garrison collapses (7,000 -> 0). Massena loses 1,435 troops in the assault. Massena marches into Milan! (796 lost to march)
  - POPUP capture_choice[capture]: Milan, Massena → secure
- CMD `Soult, move to Tyrol` → ✓ Soult moves from Munich to Tyrol (393 lost to march)
- CMD `Davout, move to Tyrol` → ✓ Davout moves from Munich to Tyrol (312 lost to march)
- CMD `Deroy, move to Munich` → ✓ Deroy moves from Swabia to Munich (374 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 9 ended. Turn 10 begins!
- SPENT 200g on this turn's orders
- enemy phase: 4 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Bohemia into Bohemia unopposed! (277 lost to march — forward supply lines reduce losses) C…
  - 🏴 Austria: ArchdukeCharles marches from Bohemia into Bohemia unopposed! (277 lost to march — forward supply lines reduce losses) Captured: France → Austria
  - verbs: move×1, attack×1, fortify×1, wait×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Deroy seeks an audience → acknowledge
  -     ↳ Deroy's grievance runs its course.
- LEDGER treasury 20046 · net +1596 · threat 97 · provinces 29 · ceiling 31881 · army 104937 · vassals Bavaria 100 · Hesse 38 · Holland 91 · Kingdom of Italy 97 · Saxony 38 · Switzerland 88
  - NET income 3458 · trade 437 · admin 50 · tribute 1313 · upkeep 816 · charges 2432 · occupation 105 · blockade 219 · admiralty 90
- DISPATCH: Sire — Marshal Ney has been taken. Austria holds him prisoner.
  - TURN EVENTS 11
- DIPLO +6 medium/low (enemy_marshal_commissioned, diplomatic_vassal_courting ×2, diplomatic_dp_regen, diplomatic_vassal_unrest ×2)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — France is not forgiven
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG design_promoted: REVANCHE: Spain swears to retake Aragon and 1 more — Britain is not forgiven
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Austria rebuffs Prussia and Naples (open borders agreement)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (open borders agreement)

---
finished: **completed** · commands 7 · popups 4 · battles 0
