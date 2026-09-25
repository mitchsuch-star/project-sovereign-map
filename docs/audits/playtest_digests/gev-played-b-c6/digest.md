# Playtest digest — gev-played-cB6

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "insist", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "proceed", "interrupt": "first", "last_stand": "breakout", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "client_petition": "grant", "settlement": "decline"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 10 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `7f6e67358f01` (dirty) · content `ccdea5f5afcf` · driver `196c4ee545c1`
  - loaded save `save_cB5.json` → Loaded: Autosave - Turn 10

## Turn 10 — Early February 1806
- CMD `invest in Hesse` → ✓ Invested in Hesse: +10 loyalty (38 → 48). Cost: 1 DP + 200g. Cooldown: 3 turns.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Deroy seeks an audience → acknowledge
  -     ↳ Deroy's grievance runs its course.
- CMD `Deroy, move to Tyrol` → ✓ Deroy moves from Munich to Tyrol (367 lost to march)
- CMD `Massena, move to Tyrol` → ✓ Massena moves from Milan to Tyrol (1,459 lost to march)
- CMD `Napoleon, move to Munich` → ✓ Napoleon moves from Swabia to Munich (132 lost to march)
- CMD `Davout, fortify` → ✓ Davout fortifies position at Tyrol. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifie…
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 10 ended. Turn 11 begins!
- SPENT 200g on this turn's orders
- enemy phase: 7 actions, 3 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Castanos marches from Galicia into Leon unopposed! (130 lost to march) Captured: Britain → Spain · Castanos executes a brilliant maneuver! Castanos gains the advantage over Paget. Casualties: Castanos 622, Paget 1,852.… · Castanos holds them at Asturias while allies attack from Leon! (+1 coordination)
  - 🏴 Spain: Castanos marches from Galicia into Leon unopposed! (130 lost to march) Captured: Britain → Spain
  - 🏴 Spain: [!] Paget's troops are BROKEN (morale 0%)! FORCED RETREAT! Asturias has been captured by Spain!
  - ⚔ Castanos (lost 622) vs Paget (lost 1852) — An aggressive stance invites disaster when one is not the attacker, Sire. Paget paid the price.
  - ⚔ Castanos (lost 293) vs Paget (lost 1480) — Paget's aggressive posture left the troops exposed when Castanos's attack came. And Paget was taken on that field — Spa…
  - verbs: attack×3, move×1, stance_change×1, fortify×1, wait×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 21488 · net +1415 · threat 95 · provinces 29 · ceiling 31739 · army 97495 · vassals Bavaria 100 · Hesse 41 · Holland 91 · Kingdom of Italy 99 · Saxony 30 · Switzerland 87
  - NET income 3459 · trade 437 · admin 50 · tribute 1316 · upkeep 744 · charges 2689 · occupation 105 · blockade 219 · admiralty 90
- DISPATCH: Sire — Leon has been taken by Britain.
  - TURN EVENTS 8
- DIPLO +4 medium/low (diplomatic_vassal_courting ×2, diplomatic_dp_regen, diplomatic_vassal_unrest)
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
  - LOG ai_ai_proposal_refused: 7 approaches rebuffed, chiefly from Austria and Prussia (open borders agreement)

## Turn 11 — Late February 1806
- CMD `Soult, attack Archduke Charles` → ✓ MUSTER — Soult (17,422; 51,719 if all march, up to 54,503 if every corps arrives) vs Archduke Charles (24,976 men) at Bohemia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Soult (lost 1266, own corps) vs Archduke Charles (lost 2010, own corps) — Lannes and Massena arrived to reinforce Soult, but Bernadotte and Deroy failed to reach the field in time.
- CMD `Napoleon, move to Tyrol` → ✓ Napoleon moves from Munich to Tyrol (129 lost to march)
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 13.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 1 action unused) Turn 12 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, fortify×1
- ENVOYS WAITING 1 · Naples open borders
- LEDGER treasury 22568 · net +1082 · threat 93 · provinces 28 (-1) · ceiling 30121 · army 88382 · vassals Bavaria 100 · Hesse 34 · Holland 91 · Kingdom of Italy 100 · Saxony 22 · Switzerland 86
  - NET income 3261 · trade 437 · admin 50 · tribute 1373 · upkeep 680 · charges 2945 · occupation 105 · blockade 219 · admiralty 90
- DISPATCH: Sire — Corsica has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there force…
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Corsica.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +6 medium/low (diplomatic_vassal_courting ×2, diplomatic_dp_regen, diplomatic_vassal_unrest ×2, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (300g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)

---
finished: **completed** · commands 12 · popups 3 · battles 3
