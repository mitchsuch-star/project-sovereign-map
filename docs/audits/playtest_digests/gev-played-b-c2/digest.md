# Playtest digest — gev-played-cB2

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "proceed", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "client_petition": "grant", "settlement": "decline"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 5 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `7f6e67358f01` (dirty) · content `ccdea5f5afcf` · driver `196c4ee545c1`
  - loaded save `save_cB1.json` → Loaded: Autosave - Turn 5

## Turn 5 — Late November 1805
- CMD `vassalize Hesse` → ✓ Hesse has become a Satellite vassal of France (loyalty: 60).
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- CMD `vassalize Saxony` → ✓ Saxony has become a Satellite vassal of France (loyalty: 60).
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Davout, attack Archduke John` → ✓ MUSTER — Davout (18,248; 40,858 if all march, up to 52,201 if every corps arrives) vs Archduke John (18,075 men) at Tyrol — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 1017, own corps) vs Archduke John (lost 3945) — Ney and Lannes's timely arrival aided Davout. Soult, Murat and Deroy, however, were conspicuously absent.
- CMD `Bernadotte, move to Franconia` → ✓ Bernadotte moves from Munich to Franconia (156 lost to march)
- CMD `Murat, move to Swabia` → ✓ Murat moves from Munich to Swabia (84 lost to march)
- CMD `Deroy, move to Swabia` → ✓ Deroy moves from Munich to Swabia (205 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 5 ended. Turn 6 begins!
- enemy phase: 4 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn strikes back after successfully defending!
  - ⚔ Archduke John (lost 5910) vs Massena (lost 863) — An exemplary engagement by Massena. The outcome was never in doubt.
  - verbs: break_square×1, move×1, attack×1, recruit×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 12668 · net +3014 · threat 91 · provinces 28 · ceiling 58054 · army 152541 · vassals Bavaria 84 · Hesse 59 · Holland 99 · Kingdom of Italy 99 · Saxony 58 · Switzerland 91
  - NET income 3400 · trade 437 · admin 50 · tribute 1640 · upkeep 1496 · charges 708 · blockade 219 · admiralty 90
- DISPATCH: Sire — Marshal Massena holds the field at Piedmont — Archduke John's corps is broken and flees.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 4
- DIPLO +4 medium/low (diplomatic_carved_vassal_created ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Austria rebuffs Prussia and Naples (open borders agreement)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 17 approaches rebuffed, chiefly from Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 6 — Early December 1805
  - MAILBOX #9 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #9 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +9 (91 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Ney, move to Tyrol` → ✗ Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke John.
- CMD `Soult, move to Tyrol` → ✗ Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke John.
- CMD `Davout, move to Tyrol` → ✗ Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke John.
- CMD `Lannes, move to Tyrol` → ✗ Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke John.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 4 actions unused) Turn 7 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Bernadotte. Casualties: A…
  - ⚔ Archduke Charles (lost 1663) vs Bernadotte (lost 4581) — Bernadotte stood alone, Sire. Ney, Soult, Lannes and Deroy never came.
  - verbs: unfortify×1, move×1, attack×1
- LEDGER treasury 15264 · net +2617 · threat 89 · provinces 28 (+0) · ceiling 50817 · army 144334 · vassals Bavaria 87 · Hesse 55 · Holland 97 · Kingdom of Italy 97 · Saxony 53 · Switzerland 97
  - NET income 3400 · trade 437 · admin 50 · tribute 1271 · upkeep 1256 · charges 976 · blockade 219 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a quarter of his corps — 4,581 men — lost in a single action.
  - RAIL design_promoted: REVANCHE: Spain will not forgive Britain the loss of Aragon and 1 more province. A new design hardens in their court.
  - TURN EVENTS 5
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

---
finished: **completed** · commands 15 · popups 4 · battles 3
