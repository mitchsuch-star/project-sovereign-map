# Playtest digest — gev-played-cB3

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "proceed", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "client_petition": "grant", "settlement": "decline"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 7 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `7f6e67358f01` (dirty) · content `ccdea5f5afcf` · driver `196c4ee545c1`
  - loaded save `save_cB2.json` → Loaded: Autosave - Turn 7

## Turn 7 — Late December 1805
- CMD `Soult, attack Archduke Charles` → ✓ MUSTER — Soult (23,654; 49,935 if all march, up to 74,590 if every corps arrives) vs Archduke Charles (36,422 men) at Franconia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Soult (lost 1743, own corps) vs Archduke Charles (lost 5791) — Lannes and Napoleon arrived to reinforce Soult, but Ney, Davout, Murat and Deroy failed to reach the field in time.
- CMD `Ney, move to Tyrol` → ✓ Ney moves from Munich to Tyrol. Tyrol falls to France! (was Austria) (289 lost to march)
  - POPUP capture_choice[capture]: Tyrol, Ney → secure
- CMD `Lannes, move to Tyrol` → ✓ Lannes moves from Munich to Tyrol (204 lost to march)
- CMD `Massena, move to Milan` → ✓ Massena moves from Piedmont to Milan (997 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. Turn 8 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending!
  - 🏴 Austria: [!] Bernadotte's troops are BROKEN (morale 0%)! FORCED RETREAT! Franconia has been captured by Austria!
  - ⚔ Archduke Charles (lost 733) vs Bernadotte (lost 4659) — Bernadotte stood alone, Sire. Ney, Soult and Deroy never came.
  - verbs: attack×1, form_square×1
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Lannes: Murat turns openly discontent (trust -3; expect defiance).
  - POPUP diplomatic_dialogue: Bavaria, client_petition #11 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to Bavaria. Loyalty +10 (90 → 100); bond 60 → 60 (+3 a turn). Cost: 1 DP. Our net rises by 36g a turn — 33g of income forfeited, 52g of occupation relieved, 25g returned as tribute at today's 75% rate, the force limit falls 2,500 (+8g surcharge). → display-only
- ENVOYS WAITING 1 · Bavaria client petition
- LEDGER treasury 17277 · net +2659 · threat 89 · provinces 28 · ceiling 49235 · army 132522 · vassals Bavaria 100 · Hesse 51 · Holland 95 · Kingdom of Italy 97 · Saxony 48 · Switzerland 94
  - NET income 3400 · trade 437 · admin 50 · tribute 1301 · upkeep 1024 · charges 1271 · requisitions 75 · blockade 219 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Bavaria has arrived with a petition.
  - TURN EVENTS 7
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG design_promoted: REVANCHE: Spain swears to retake Aragon and 1 more — Britain is not forgiven
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Austria rebuffs Prussia and Naples (open borders agreement)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 17 approaches rebuffed, chiefly from Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)

---
finished: **completed** · commands 6 · popups 5 · battles 2
