# Playtest digest — gev-played-cB4

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "proceed", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "client_petition": "grant", "settlement": "decline"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 8 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `7f6e67358f01` (dirty) · content `ccdea5f5afcf` · driver `196c4ee545c1`
  - loaded save `save_cB3.json` → Loaded: Autosave - Turn 8

## Turn 8 — Early January 1806
  - MAILBOX #10 Bavaria incoming_proposal: Bavaria — Client's Petition → activated
  - POPUP diplomatic_dialogue: Bavaria, client_petition #11 → grant the petition
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Lannes: They settle into cold war.
  - POPUP proposal_result: Tyrol is ceded to Bavaria. Loyalty +10 (90 → 100); bond 60 → 60 (+3 a turn). Cost: 1 DP. Our net rises by 36g a turn — 33g of income forfeited, 52g of occupation relieved, 25g returned as tribute at today's 75% rate, the force limit falls 2,500 (+8g surcharge). → display-only
- CMD `Soult, attack Archduke Charles` → ✓ MUSTER — Soult (21,691; 38,878 if all march, up to 61,779 if every corps arrives) vs Archduke Charles (29,898 men) at Franconia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Soult (lost 2004, own corps) vs Archduke Charles (lost 2836, own corps) — Lannes, Murat and Napoleon arrived to reinforce Soult, but Ney, Davout and Deroy failed to reach the field in time.
- CMD `Massena, attack Milan` → ✓ Massena assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). Massena loses 2,012 troops. Garrison holds — 5,000 defenders remain.
- CMD `Ney, attack Archduke John` → ✓ MUSTER — Ney (13,904) vs Archduke John (small force) at Bohemia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 835) vs Archduke John (lost 3319) — A decisive victory for Ney! Archduke John was thoroughly outmatched.
  - POPUP capture_choice[capture]: Bohemia, Ney → secure
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 1 action unused) Turn 9 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending!
  - ⚔ Archduke Charles (lost 183) vs Ney (lost 5214) — Ney's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: break_square×1, attack×1
- ORDER Ney [awaiting_response]: Ney is cornered at Bohemia with 3,840 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - ⚡ AUTONOMOUS: [Shield] Archduke Charles steps forward to cover Archduke John's retreat! "Archduke John is in no condition to fight - I'll handle this!"
  - ⚔ Murat (lost 2127, own corps) vs Archduke Charles (lost 519) — Reinforcements from Ney bolstered Murat's position — though Davout, Soult and Deroy never arrived, Sire.
  - POPUP strategic_interrupt: Ney, last_stand, Ney is cornered at Bohemia with 3,840 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 18473 · net +1858 · threat 92 · provinces 29 · ceiling 32672 · army 110168 · vassals Bavaria 100 · Hesse 44 · Holland 90 · Kingdom of Italy 94 · Saxony 35 · Switzerland 88
  - NET income 3400 · trade 437 · admin 50 · tribute 1307 · upkeep 848 · charges 2154 · requisitions 75 · occupation 100 · blockade 219 · admiralty 90
- DISPATCH: Sire — Ney, crowned last turn, has been beaten in the field.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain. Offering 2469 gold.
  - RAIL design_promoted: REVANCHE: Austria will not forgive France the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 8
- DIPLO +6 medium/low (diplomatic_we_threshold, diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
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
finished: **completed** · commands 5 · popups 7 · battles 4
