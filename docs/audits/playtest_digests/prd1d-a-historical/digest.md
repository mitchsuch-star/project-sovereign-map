# Playtest digest — prd1d-a

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "proceed", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `17b2ab9909bd` (dirty) · content `f8f301d236a2` · driver `f870e9ba2f5e`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 78,676 with the corps likely to arrive, up to 96,789 if all march) vs Mack (large force) at Swabia — the balance of force looks favora…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1850, own corps) vs Mack (lost 15045) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Soult, Murat and Bernadotte never arr…
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles engages in solid combat. Brutal stalemate between ArchdukeCharles and Massena. Heavy casualties on both…
  - ⚔ Archduke Charles (lost 4958) vs Massena (lost 5043) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - verbs: attack×1, wait×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 2454 · net +2213 · threat 76 · provinces 28 · ceiling 56681 · army 176527 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 99
  - NET income 3400 · trade 400 · admin 50 · tribute 895 · upkeep 2224 · charges 18 · blockade 200 · admiralty 90
- DISPATCH: Supply cost you 1,099 men, at Swabia.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +5 medium/low (diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (21,398; expect about 89,873 with the corps likely to arrive, up to 99,901 if all march) vs Mack (substantial force) at Munich — the balance of force looks …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 610, own corps) vs Mack (lost 21832) — Davout and Massena arrived to reinforce Ney, but Napoleon failed to reach the field in time.
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (22,844; expect about 33,229 with the corps likely to arrive, up to 44,912 if all march) vs Mack (large force) at Tyrol — the balance of force looks even.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 8051) vs Archduke Charles (lost 1192, own corps) — Davout stood alone, Sire. Ney never came.
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✗ Murat is already in Franche-Comte.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 2 actions unused) Turn 3 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · Deroy launches a decisive assault. ArchdukeJohn holds the line. Casualties: Deroy 3,394, ArchdukeJohn 1,572. Both armie… · Deroy engages in solid combat. ArchdukeJohn holds the line. Casualties: Deroy 3,180, ArchdukeJohn 1,146. Both armies re…
  - ⚔ Archduke Charles (lost 1879) vs Bernadotte (lost 5468) — Bernadotte stood alone, Sire. Ney never came.
  - ⚔ Deroy (lost 3394) vs Archduke John (lost 1572) — Archduke John's fortifications held firm, Sire. Deroy broke against our walls.
  - ⚔ Deroy (lost 3180) vs Archduke John (lost 1146) — The prepared defenses proved their worth. Deroy could not dislodge Archduke John.
  - verbs: attack×3, fortify×1, wait×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 4503 · net +2636 · threat 82 · provinces 28 (+0) · ceiling 50263 · army 159208 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 94
  - NET income 3400 · trade 450 · admin 50 · tribute 901 · upkeep 1706 · charges 144 · blockade 225 · admiralty 90
- DISPATCH: Sire — Davout's corps has been broken at Munich. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +7 medium/low (diplomatic_treaty_signed ×3, diplomatic_we_threshold ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 26 approaches from Prussia, Bavaria and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (19,952; expect about 52,723 with the corps likely to arrive, up to 54,026 if all march) vs Mack (13,064 men) at Tyrol — the balance of force looks favorabl…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 493, own corps) vs Mack (lost 6942, own corps) — Massena's timely arrival bolstered Ney's position. Well-coordinated, Sire.
  - POPUP capture_choice[capture]: Tyrol, Ney → secure
- CMD `Davout, attack Mack` → ✗ Davout is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Rhineland to Swabia (166 lost to march)
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 712 gold (×3 at war) (×1.19 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 2 actions unused) Turn 4 begins!
- SPENT 712g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 6416 · net +2397 · threat 90 · provinces 29 (+1) · ceiling 32578 · army 159127 · vassals Holland 98 · Kingdom of Italy 98 · Switzerland 93
  - NET income 3420 · trade 525 · admin 50 · tribute 905 · upkeep 1694 · charges 404 · occupation 52 · blockade 263 · admiralty 90
- DISPATCH: Sire — Marshal Ney holds the field at Tyrol — Mack's corps is driven from Tyrol yet again — broken, and fleeing.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 6
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG ai_ai_proposal_refused: 25 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✗ No intelligence on Mack's position, Sire. Scout for him before Ney can give chase.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Franche-Comte. Defense bonus: +7% (grows +3% per t…
- CMD `Massena, move to Tyrol` → ✗ Massena is already in Tyrol.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 actions unused) Turn 5 begins!
- enemy phase: 5 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Vienna into Bohemia unopposed! (1,269 lost to march) Captured: Bavaria → Austria · ArchdukeCharles launches a decisive assault. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCharle…
  - 🏴 Austria: ArchdukeCharles marches from Vienna into Bohemia unopposed! (1,269 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Carniola. (1,425 lost to march) Carniola has been captured by Austria!
  - ⚔ Archduke Charles (lost 1469) vs Deroy (lost 4865) — The hills were ours, but Archduke Charles took them. Deroy's position was overrun.
  - verbs: attack×2, fortify×1, stance_change×1, wait×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 8991 · net +2236 · threat 88 · provinces 29 (+0) · ceiling 32569 · army 157245 · vassals Holland 98 · Kingdom of Italy 98 · Switzerland 91
  - NET income 3421 · trade 587 · admin 50 · tribute 910 · upkeep 1634 · charges 662 · occupation 52 · blockade 294 · admiralty 90
- DISPATCH: Sire — Bohemia has been taken by Austria.
  - TURN EVENTS 6
- DIPLO +3 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Denmark rebuffs Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 2 more — Bavaria is not forgiven
  - LOG ai_ai_proposal_refused: 28 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)

## Turn 5 — Late November 1805
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (17,985) vs Archduke Charles (38,163 men) at Carniola — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1891, own corps) vs Archduke Charles (lost 1682) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
- CMD `Lannes, attack Mack` → ✗ No intelligence on Mack's position, Sire. Scout for him before Lannes can give chase.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (990 lost to march)
- CMD `Murat, move to Swabia` → ✓ Murat moves from Franche-Comte to Swabia (308 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 1 action unused) Turn 6 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, wait×1, recruit×1
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 11529 · net +2599 · threat 86 · provinces 29 (+0) · ceiling 47219 · army 147100 · vassals Holland 96 · Kingdom of Italy 96 · Switzerland 87
  - NET income 3465 · trade 587 · admin 50 · tribute 914 · upkeep 1310 · charges 693 · occupation 30 · blockade 294 · admiralty 90
- DISPATCH: Sire — Ney, crowned five turns ago, has been beaten in the field.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria

## Turn 6 — Early December 1805
  - MAILBOX #8 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #9 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to the Kingdom of Italy. Loyalty +4 (96 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. Our net rises by 2g a turn — 65g of income forfeited, 30g of occupation relieved, 49g returned as tribute at today's 75% rate, the force limit falls 2,500 (+12g surcharge). → display-only
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! ArchdukeCharles is at Carniola, just one region away.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 2 actions unused) Turn 7 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn's forces press forward aggressively. Ney holds the line. Casualties: ArchdukeJohn 4,948, Ney's army 1,031.…
  - ⚔ Archduke John (lost 4948) vs Ney (lost 367, own corps) — A decisive victory for Ney! Archduke John was thoroughly outmatched.
  - verbs: attack×1, wait×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
  -     ↳ Massena's grievance runs its course.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #10 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (86 → 96); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 14141 · net +2233 · threat 84 · provinces 28 (-1) · ceiling 43210 · army 142744 · vassals Holland 97 · Kingdom of Italy 100 · Switzerland 96
  - NET income 3400 · trade 587 · admin 50 · tribute 708 · upkeep 1196 · charges 932 · blockade 294 · admiralty 90
- DISPATCH: Sire — Leon has been taken by Britain.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 7 — Late December 1805
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (15,188) vs Archduke Charles (36,481 men) at Carniola — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2112, own corps) vs Archduke Charles (lost 762) — Massena marched to Ney's guns as ordered. It was not enough.
- CMD `Davout, move to Bohemia` → ✓ Davout begins marching to Bohemia (distance: 3). Moved to Swabia. Route: Swabia -> Franconia -> Bohemia.
- CMD `Murat, attack Archduke Charles` → ✗ Not enough actions for a strategic pursuit! Need 2, have 1.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 1 action unused) Turn 8 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Bernadotte. Casualties: A…
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Tyrol. (2,110 lost to march) Tyrol has been captured by Austria!
  - ⚔ Archduke Charles (lost 551) vs Massena (lost 10904) — Massena stood alone, Sire. Bernadotte never came.
  - ⚔ Archduke Charles (lost 719) vs Bernadotte (lost 6107) — Where was Soult? Bernadotte held the field alone — reinforcement never came.
  - verbs: attack×2, unfortify×1, wait×1
- ORDER Davout [active]: Davout is marching to Bohemia (3 turns remaining).
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Austria, armistice_losing #11 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 15371 · net +2137 · threat 82 · provinces 28 (+0) · ceiling 36651 · army 112952 · vassals Holland 91 · Kingdom of Italy 95 · Switzerland 89
  - NET income 3400 · trade 587 · admin 50 · tribute 698 · upkeep 872 · charges 1342 · blockade 294 · admiralty 90
- DISPATCH: Sire — Ney's corps has been broken at Tyrol. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 11
- DIPLO +4 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Austria (open borders agreement)

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✗ Cannot attack ArchdukeCharles — armistice with Austria (5 turns remaining).
- CMD `Ney, fortify` → ✗ Ney is recovering from retreat and cannot fortify. Recovery: 2 turns remaining.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shift…
- CMD `Massena, move to Milan` → ✓ Massena begins marching to Milan (distance: 2). Moved to Munich. Route: Munich -> Milan.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 1 action unused) Turn 9 begins!
- enemy phase: 7 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Franconia into Franconia unopposed! (916 lost to march) Captured: Bavaria → Austria · ArchdukeCharles's forces advance steadily. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCharles …
  - 🏴 Austria: ArchdukeCharles marches from Franconia into Franconia unopposed! (916 lost to march) Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 1614) vs Deroy (lost 3564) — Deroy held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: attack×2, move×1, garrison×1, retreat×1, stance_change×1, wait×1
- ORDER Massena [active]: Massena is marching to Milan (2 turns remaining).
- LEDGER treasury 17526 · net +1932 · threat 80 · provinces 28 (+0) · ceiling 36169 · army 107415 · vassals Holland 91 · Kingdom of Italy 94 · Switzerland 88
  - NET income 3400 · trade 587 · admin 50 · tribute 703 · upkeep 816 · charges 1608 · blockade 294 · admiralty 90
- DISPATCH: Sire — Franconia has been taken by Austria.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - TURN EVENTS 6
- COURTS: The court of Austria eases over Redeem Italy — an ultimatum is now the length of its tether.
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 10 approaches from Austria and Prussia are rebuffed (defensive alliance)

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Lannes, move to Bohemia` → ✗ Lannes is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 11.
- CMD `recruit 10000 cavalry with Murat` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 actions unused) Turn 10 begins!
- enemy phase: 5 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Deroy. Casualties: Archdu… · ArchdukeCharles assaults the Munich garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 3,674 troops. G… · Castanos's forces press forward aggressively. Castanos gains the advantage over Paget. Casualties: Castanos 676, Paget … · Castanos holds them at Leon while allies attack from Aragon! (+1 coordination)
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Swabia. (545 lost to march) Swabia has been captured by Austria!
  - 🏴 Spain: [!] Paget's troops are BROKEN (morale 0%)! FORCED RETREAT! Leon has been captured by Spain!
  - ⚔ Archduke Charles (lost 549) vs Deroy (lost 7643) — A grievous defeat for Deroy, Sire. The losses are severe.
  - ⚔ Castanos (lost 676) vs Paget (lost 1674) — An aggressive stance invites disaster when one is not the attacker, Sire. Paget paid the price.
  - ⚔ Castanos (lost 324) vs Paget (lost 1610) — Paget's aggressive posture left the troops exposed when Castanos's attack came.
  - verbs: attack×4, move×1
- ORDER Ney [continues]: Ney marches to Swabia. 1 region to Rhineland.
- ORDER Massena [continues]: Massena hears cannon fire at Swabia but cannot answer it — no road leads there. His march continues.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Ney: They settle into cold war.
  - POPUP diplomatic_dialogue: incoming_settlement_offer #12 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #13 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified: France vs Austria + Britain + Russia (7 pairs resolved). Status quo: Franconia and Swabia stay Austrian by the treaty. → display-only
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 19452 · net +3795 · threat 78 · provinces 28 (+0) · ceiling 335666 · army 101549 · vassals Holland 91 · Kingdom of Italy 93 · Switzerland 87
  - NET income 3400 · trade 623 · admin 50 · tribute 707 · upkeep 776 · charges 209
- DISPATCH: Sire — Swabia has been taken by Austria.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 9
- DIPLO +4 medium/low (diplomatic_we_threshold ×2, diplomatic_dp_regen, agenda_shift)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 78 to 39.

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney moves from Swabia to Franconia (118 lost to march)
- CMD `Davout, fortify` → ✓ Davout fortifies position at Swabia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Munich.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 actions unused) Turn 11 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×2, wait×1
- ORDER Bernadotte [completed]: Bernadotte arrives at Franche-Comte. Bernadotte: "Accomplished as ordered. The army is intact."
- ORDER Lannes [error]: Lannes could not advance toward Franche-Comte.
- ORDER Massena [completed]: Massena arrives at Milan. Massena: "Accomplished. The men want a battle, not another road."
- ORDER Murat [error]: Murat could not advance toward Franche-Comte.
- ORDER Napoleon [completed]: Napoleon arrives at Franche-Comte.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Bernadotte and Ney: They settle into cold war.
  - POPUP diplomatic_dialogue: Holland, client_petition #14 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (89 → 99); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 23284 · net +3449 · threat 39 · provinces 28 (+0) · ceiling 310666 · army 97259 · vassals Holland 99 · Kingdom of Italy 94 · Switzerland 86
  - NET income 3400 · trade 623 · admin 50 · tribute 375 · upkeep 744 · charges 255
- DISPATCH: Sire — Davout, Soult, Lannes and Murat have been 5 turns over what Swabia can feed. 14,868 men. The country will ask where the army went. No depot may be laid at Swabia — not controlled by France. Rh…
  - RAIL settlement_summary: Settlement of France + Spain + Holland + Bavaria + Kingdom of Italy vs Britain + Austria + Russia: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 9
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: And 3 other courts stir at their own designs.
- DIPLO +5 medium/low (diplomatic_coalition_dissolved, diplomatic_dp_regen, blockade_broken ×3)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_ai_proposal_refused: 17 approaches rebuffed, chiefly from Bavaria (open borders agreement)

## Turn 11 — Late February 1806
- CMD `Ney, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Lannes, attack Archduke John` → ✗ Lannes is fortified at Swabia and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Swabia to Franconia (158 lost to march)
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 1 action unused) Turn 12 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 26749 · net +3424 · threat 39 · provinces 28 (+0) · ceiling 312000 · army 95010 · vassals Holland 98 · Kingdom of Italy 95 · Switzerland 85
  - NET income 3400 · trade 623 · admin 50 · tribute 375 · upkeep 728 · charges 296
- DISPATCH: Sire — Davout, Soult and Lannes have been 6 turns over what Swabia can feed. 11,433 men. The country will ask where the army went. No depot may be laid at Swabia — not controlled by France. Rhineland…
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Bavaria (open borders agreement)

## Turn 12 — Early March 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, unfortify×1, wait×1
- LEDGER treasury 30189 · net +3398 · threat 39 · provinces 28 (+0) · ceiling 313333 · army 92940 · vassals Holland 97 · Kingdom of Italy 96 · Switzerland 84
  - NET income 3400 · trade 623 · admin 50 · tribute 375 · upkeep 712 · charges 338
- DISPATCH: Sire — Davout, Soult and Lannes have been 7 turns over what Swabia can feed. 7,544 men. The country will ask where the army went. No depot may be laid at Swabia — not controlled by France. Rhineland …
  - TURN EVENTS 7
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (300g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG ai_ai_proposal_refused: Sardinia, Holland and Kingdom of Italy rebuff Bavaria (open borders agreement)

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #15 → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation #16 → force_declare_war
  - POPUP diplomatic_dialogue: proposal_confirm #17 → ally_entry_proceed_without
  - POPUP proposal_result: France declares war on Austria, shattering the Peace Treaty! Britain enters the war against France in defense of Austria! Russia enters the war against France in defense of Austria! Holland follows France into the war against Austria! KingdomOfItaly follows France into the war against Austria! Switzerland follows France into the war against Austria! → display-only
- CMD `Davout, move to Franconia` → ✗ Cannot advance while engaged with enemy forces. You may retreat to friendly territory.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 actions unused) Turn 14 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack struggles in a costly engagement. Mack gains the advantage over Ney. Casualties: Mack 1,361, Ney's army 4,574. Bot… · Mack holds them at Franconia while allies attack from Bohemia! (+1 coordination)
  - ⚔ Mack (lost 1361) vs Ney (lost 2408, own corps) — Davout marched to Ney's guns as ordered. It was not enough.
  - ⚔ Mack (lost 2182, own corps) vs Murat (lost 2636) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: attack×2, wait×1
- LEDGER treasury 31172 · net +1248 · threat 57 · provinces 28 (+0) · ceiling 48889 · army 85337 · vassals Holland 95 · Kingdom of Italy 96 · Switzerland 82
  - NET income 3400 · trade 587 · admin 50 · tribute 375 · upkeep 664 · charges 2053 · contributions 150 · requisitions 87 · blockade 294 · admiralty 90
- DISPATCH: Sire — Ney's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_alliance_cascade: Britain enters the war via alliance with Austria.
  - RAIL diplomatic_alliance_cascade: Russia enters the war via alliance with Austria.
  - RAIL diplomatic_war_declared: France has declared war on Austria, shattering the Peace Treaty, with 4 allied courts poised to follow.
  - RAIL strait_shut: THE STRAIT: the Cagliari–Corsica crossing is shut — Britain commands the water.
  - RAIL strait_shut: THE STRAIT: the Corsica–Piedmont crossing is shut — Britain commands the water.
  - RAIL strait_shut: THE STRAIT: the London–Normandy crossing is shut — Britain commands the water.
  - TURN EVENTS 9
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as war.
- COURTS: The court of Britain hardens over The Low Countries — prepared now to go as far as war.
- COURTS: And 2 other courts stir at their own designs.
- DIPLO +6 medium/low (witness_strike_recorded, diplomatic_treaty_broken ×2, diplomatic_dp_regen, sovereign_takes_field, blockade_begins)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG diplomatic_treaty_broken: France has broken the Peace Treaty with Austria by declaring war.
  - LOG defensive_cascade: Defensive cascade: Britain joins war via Austria
  - LOG defensive_cascade: Defensive cascade: Russia joins war via Austria
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_auto_join_war: Vassal Switzerland joined France's war.

## Turn 14 — Early April 1806
- CMD `declare war on Austria` → ✗ We are already at war with Austria, Sire.
- CMD `Lannes, fortify` → ✗ Lannes is already fortified at Swabia (+2% defense).
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Milan and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 actions unused) Turn 15 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack's forces advance steadily. Brutal stalemate between Mack and Murat. Heavy casualties on both sides: Mack's army 2,…
  - ⚔ Mack (lost 1890, own corps) vs Murat (lost 2720) — Neither Murat nor Mack could claim the field. The armies remain locked.
  - verbs: attack×1, wait×1
- LEDGER treasury 31978 · net +1096 · threat 55 · provinces 27 (-1) · ceiling 46547 · army 82406 · vassals Holland 95 · Kingdom of Italy 98 · Switzerland 82
  - NET income 3200 · trade 587 · admin 50 · tribute 600 · upkeep 640 · charges 2254 · contributions 150 · requisitions 87 · blockade 294 · admiralty 90
- DISPATCH: Sire — Corsica has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there force…
  - RAIL expedition_landed: THE LANDING: Paget has put 6,424 men ashore at Corsica.
  - TURN EVENTS 8
- COURTS: The court of Sweden hardens over Scourge of the Usurper — prepared now to go as far as war.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Britain lapses
  - LOG sponsorship_granted: Britain sponsors Russia against France (300g/turn)
  - LOG diplomatic_treaty_broken: Britain was forced to break the Peace Treaty with France (cascade).

## Turn 15 — Late April 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, drill` → ✗ Davout cannot drill with enemy forces nearby! Mack is at Franconia, just one region away.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 4 actions unused) Turn 16 begins!
- enemy phase: 5 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack's forces press forward aggressively. Brutal stalemate between Mack and Murat. Heavy casualties on both sides: Mack… · ArchdukeCharles marches from Lorraine into Lorraine unopposed! (373 lost to march) Captured: France → Austria · ArchdukeJohn flanks from Bohemia while allies attack from Franconia! (+1 coordination) · ArchdukeCharles launches a decisive assault. ArchdukeCharles gains the advantage over Bernadotte. Casualties: ArchdukeC…
  - 🏴 Austria: ArchdukeCharles marches from Lorraine into Lorraine unopposed! (373 lost to march) Captured: France → Austria
  - ⚔ Mack (lost 1964) vs Murat (lost 2383) — Not one corps reached Murat. Davout was expected; Murat fought the battle single-handed.
  - ⚔ Archduke John (lost 581, own corps) vs Murat (lost 1831) — Murat stood alone, Sire. Davout never came.
  - ⚔ Archduke Charles (lost 131) vs Bernadotte (lost 2163) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×4, wait×1
- LEDGER treasury 31633 · net -24 · threat 53 · provinces 26 (-1) · ceiling 31412 · army 75903 · vassals Holland 93 · Kingdom of Italy 98 · Switzerland 80
  - NET income 3042 · trade 587 · admin 50 · tribute 600 · upkeep 584 · charges 3330 · contributions 92 · requisitions 87 · blockade 294 · admiralty 90
- DISPATCH: Sire — Lorraine has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there forc…
  - TURN EVENTS 7
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses

## Turn 16 — Early May 1806
- CMD `Ney, move to Bohemia` → ✗ Cannot move into Bohemia - enemy forces present! Use ATTACK to engage Archduke John.
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while engaged with enemy forces! Enemy present: Mack. Attack or retreat first.
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 3 actions unused) Turn 17 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack struggles in a costly engagement. Brutal stalemate between Mack and Murat. Heavy casualties on both sides: Mack's … · ArchdukeJohn flanks from Bohemia while allies attack from Franconia! (+1 coordination)
  - ⚔ Mack (lost 1141, own corps) vs Murat (lost 810, own corps) — Reinforcements from Lannes bolstered Murat's position — though Davout never arrived, Sire.
  - ⚔ Archduke John (lost 310, own corps) vs Murat (lost 2190) — Where was Davout? Murat held the field alone — reinforcement never came.
  - verbs: attack×2, wait×1
- LEDGER treasury 32240 · net +755 · threat 51 · provinces 26 (+0) · ceiling 40738 · army 71378 · vassals Holland 91 · Kingdom of Italy 98 · Switzerland 78
  - NET income 3044 · trade 587 · admin 50 · tribute 600 · upkeep 544 · charges 2685 · requisitions 87 · blockade 294 · admiralty 90
- DISPATCH: Sire — Murat was mauled at Franconia: a third of his corps — 2,190 men — lost in a single action.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 5 courts rebuff Prussia (defensive alliance)

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Mun…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Munich. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, drill` → ✗ Lannes cannot drill with enemy forces nearby! Mack is at Franconia, just one region away.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Milan (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action unused) Turn 18 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack's forces press forward aggressively. Mack gains the advantage over Murat. Casualties: Mack's army 959, Murat's arm…
  - ⚔ Mack (lost 641, own corps) vs Murat (lost 637, own corps) — Lannes reached Murat in time, Sire — but even together, the field could not be held.
  - verbs: attack×1, wait×1
- ORDER Murat [awaiting_response]: Murat is cornered at Franconia with 2,432 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Murat, last_stand, Murat is cornered at Franconia with 2,432 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
- LEDGER treasury 31680 · net -410 · threat 49 · provinces 26 (+0) · ceiling 28382 · army 66313 · vassals Holland 89 · Kingdom of Italy 98 · Switzerland 76
  - NET income 3046 · trade 587 · admin 50 · tribute 600 · upkeep 504 · charges 3692 · contributions 150 · requisitions 37 · blockade 294 · admiralty 90
- DISPATCH: Sire — Archduke Charles has crossed into Rhineland. No French corps stands in his path.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✗ Marshal Murat is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Munich, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Rhineland into Rhineland unopposed! (270 lost to march) Captured: France → Austria · Mack's forces advance steadily. Ney holds the line. Casualties: Mack 3,693, Ney's army 1,047. Both armies remain in the…
  - 🏴 Austria: ArchdukeCharles marches from Rhineland into Rhineland unopposed! (270 lost to march) Captured: France → Austria
  - ⚔ Mack (lost 3693) vs Ney (lost 310, own corps) — Lannes and Napoleon arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire.
  - verbs: attack×2, fortify×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 32033 · net +702 · threat 47 · provinces 25 (-1) · ceiling 39193 · army 64357 · vassals Holland 90 · Kingdom of Italy 100 · Switzerland 77
  - NET income 2898 · trade 587 · admin 50 · tribute 937 · upkeep 480 · charges 2943 · requisitions 37 · blockade 294 · admiralty 90
- DISPATCH: Sire — Rhineland has fallen. Enemy colours fly over French homeland soil. ArchdukeCharles's corps of ~27,500 stands there. A garrison you detach (3,000 men) holds a province against a march, as does …
  - TURN EVENTS 8
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (300g/turn)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Munich. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✗ Cannot move into Franconia - enemy forces present! Use ATTACK to engage Archduke John.
- CMD `Murat, drill` → ✗ Marshal Murat is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 3 actions unused) Turn 20 begins!
- enemy phase: 5 actions, 4 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Rhineland into Gelderland unopposed! (255 lost to march) Captured: Holland → Austria · ArchdukeCharles assaults the Amsterdam garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 2,645 troops… · ArchdukeCharles assaults the Amsterdam garrison! Garrison collapses (5,000 -> 0). ArchdukeCharles loses 1,543 troops in… · ArchdukeCharles assaults the Flanders garrison! Garrison: 12,000 -> 7,855 (-4,145). ArchdukeCharles loses 4,166 troops.…
  - 🏴 Austria: ArchdukeCharles marches from Rhineland into Gelderland unopposed! (255 lost to march) Captured: Holland → Austria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -77g, Holland -125g. Captured: Holland → Austria
  - verbs: attack×4, unfortify×1
- LEDGER treasury 32095 · net +241 · threat 44 · provinces 25 (+0) · ceiling 34413 · army 63475 · vassals Holland 90 · Kingdom of Italy 100 · Switzerland 77
  - NET income 2884 · trade 549 · admin 50 · tribute 675 · upkeep 472 · charges 3117 · requisitions 37 · blockade 275 · admiralty 90
- DISPATCH: Sire — Flanders holds. Archduke Charles left 4,166 men before the works; 7,855 of ours are still under arms.
  - TURN EVENTS 4
- COURTS: The court of Sweden hardens over Scourge of the Usurper — prepared now to go as far as war.
- DIPLO +3 medium/low (diplomatic_dp_regen, balance_of_europe_shifted, diplomatic_auto_downgrade)
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 36% of active European bloc power.
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! ArchdukeJohn is at Franconia, just one region away.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: defend×1
- LEDGER treasury 32243 · net +133 · threat 41 · provinces 25 (+0) · ceiling 33479 · army 62620 · vassals Holland 90 · Kingdom of Italy 100 · Switzerland 77
  - NET income 2888 · trade 549 · admin 50 · tribute 675 · upkeep 472 · charges 3229 · requisitions 37 · blockade 275 · admiralty 90
- DISPATCH: Soult's fortifications decay: 11% → 10%
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 9 courts rebuff Austria (defensive alliance)

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✓ Ney firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Deroy at Franche-Comte instead.)
  - POPUP objection: Ney, Ney firmly objects: 'I would rather attack than sit idle.' (Trust him and he will attack Deroy at Franche-Comte instead.) → trust
- CMD `Davout, drill` → ✗ Davout cannot drill with enemy forces nearby! ArchdukeJohn is at Franconia, just one region away.
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Trust him and he will attack Deroy at Franche-Comte instead.)
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Trust him and he will attack Deroy at Franche-Comte instead.) → trust
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier checks the order of battle. 'No marshal of infantry can reach Paris, Sire — none of ours stands within reach.' Bernadotte commands our foot at Nivernais — march…
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 actions unused) Turn 22 begins!
- enemy phase: 1 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — Mack delivers an effective strike. Ney holds the line. Casualties: Mack 4,619, Ney's army 829. Both armies remain in th…
  - ⚔ Mack (lost 4619) vs Ney (lost 246, own corps) — An exemplary engagement by Ney. The outcome was never in doubt.
  - verbs: attack×1
- LEDGER treasury 32250 · net +43 · threat 38 · provinces 25 (+0) · ceiling 32634 · army 60987 · vassals Holland 91 · Kingdom of Italy 100 · Switzerland 78
  - NET income 2892 · trade 549 · admin 50 · tribute 675 · upkeep 456 · charges 3339 · requisitions 37 · blockade 275 · admiralty 90
- DISPATCH: Sire — Marshal Ney holds the field at Munich — Mack's corps is driven from Munich yet again — broken, and fleeing.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Marshal Murat is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 actions unused) Turn 23 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×3
- ENVOYS WAITING 1 · Austria settlement offer
- LEDGER treasury 32200 · net -44 · threat 35 · provinces 25 (+0) · ceiling 31806 · army 60206 · vassals Holland 91 · Kingdom of Italy 100 · Switzerland 78
  - NET income 2896 · trade 549 · admin 50 · tribute 675 · upkeep 456 · charges 3430 · requisitions 37 · blockade 275 · admiralty 90
- DISPATCH: Supply cost you 781 men, at Munich.
  - RAIL settlement_offer_arrival: Austria has offered terms to settle France vs Austria. Asking 6907 gold.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
  - MAILBOX #13 Austria incoming_settlement_offer: Austria — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #18 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #19 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified: France vs Austria + Britain + Russia (6 pairs resolved). Status quo: Lorraine and Rhineland stay Austrian by the treaty. Status quo: Corsica stays British by the treaty. Status quo: Amsterdam and Gelderland stay Austrian by the treaty. → display-only
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Munich. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, unfortify` → ✗ Lannes is not currently fortified.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 2 actions unused) Turn 24 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 28744 · net +3410 · threat 34 · provinces 25 (+0) · ceiling 312833 · army 64448 · vassals Holland 89 · Kingdom of Italy 100 · Switzerland 76
  - NET income 2900 · trade 585 · admin 50 · tribute 675 · upkeep 480 · charges 320
- DISPATCH: Sire — Soult is no nearer home, and the safe passage runs out in 2 turns. After that his corps will be interned where it stands.
  - RAIL settlement_summary: Settlement of France + Holland + Kingdom of Italy + Switzerland vs Austria + Britain + Russia: Gold indemnity: 6907 gold from France to Austria.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 4
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: And 3 other courts stir at their own designs.
- DIPLO +2 medium/low (diplomatic_dp_regen, blockade_broken)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sweden (defensive alliance)

## Turn 24 — Early September 1806
  - MAILBOX #14 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #20 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (600g forgone). Loyalty +10 (89 → 99); bond 5 → 25 (+1 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 26.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 2 actions unused) Turn 25 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #21 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (74 → 84); bond 5 → 25 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 32079 · net +3070 · threat 33 · provinces 25 (+0) · ceiling 287833 · army 63714 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 84
  - NET income 2900 · trade 585 · admin 50 · tribute 375 · upkeep 480 · charges 360
- DISPATCH: Sire — Soult is no nearer home, and the safe passage runs out in 1 turn. After that his corps will be interned where it stands.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 9
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Munich. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Munich. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 35157 · net +3041 · threat 32 · provinces 25 (+0) · ceiling 288500 · army 63001 · vassals Holland 97 · Kingdom of Italy 100 · Switzerland 83
  - NET income 2900 · trade 585 · admin 50 · tribute 375 · upkeep 472 · charges 397
- DISPATCH: Sire — Soult is no nearer home, and the safe passage runs out in 0 turns. After that his corps will be interned where it stands.
  - TURN EVENTS 10
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 38206 · net +3180 · threat 31 · provinces 25 (+0) · ceiling 303166 · army 40762 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 82
  - NET income 2900 · trade 585 · admin 50 · tribute 375 · upkeep 296 · charges 434
- DISPATCH: Sire — Marshal Soult's corps was interned at Swabia by Austria — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, balance_of_europe_shifted)
  - LOG balance_of_europe_shifted: British-led alignment leads the current largest alignment at 42% of active European bloc power.
  - LOG ai_ai_proposal_refused: Hanover, Papal States and Sardinia rebuff Austria (defensive alliance)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Munich. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Munich. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cann…
- CMD `Soult, unfortify` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Munich, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 2 actions unused) Turn 28 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 41386 · net +3142 · threat 30 · provinces 25 (+0) · ceiling 303166 · army 40092 · vassals Holland 95 · Kingdom of Italy 100 · Switzerland 81
  - NET income 2900 · trade 585 · admin 50 · tribute 375 · upkeep 296 · charges 472
- DISPATCH: Sire — Marshal Soult's corps was interned at Swabia by Austria — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 1 action unused) Turn 29 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 44528 · net +3104 · threat 29 · provinces 25 (+0) · ceiling 303166 · army 39442 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 80
  - NET income 2900 · trade 585 · admin 50 · tribute 375 · upkeep 296 · charges 510
- DISPATCH: DRILL COMPLETE: Davout's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 10).
  - TURN EVENTS 8
- COURTS: The court of Britain eases over The Low Countries — service to the strong is now the length of its tether.
- COURTS: The court of Austria eases over Redeem Italy — alliance is now the length of its tether.
- COURTS: And 1 other court stirs at its own design.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Munich. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Munich. Army is now mobile.
- CMD `Soult, drill` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Munich. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 1 action unused) Turn 30 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 47640 · net +3075 · threat 28 · provinces 25 (+0) · ceiling 303833 · army 38811 · vassals Holland 93 · Kingdom of Italy 100 · Switzerland 79
  - NET income 2900 · trade 585 · admin 50 · tribute 375 · upkeep 288 · charges 547
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sweden (defensive alliance)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat is fortified and cannot drill. Abandon fortification first.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Munich, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 50731 · net +3054 · threat 27 · provinces 25 (+0) · ceiling 305166 · army 38200 · vassals Holland 92 · Kingdom of Italy 100 · Switzerland 78
  - NET income 2900 · trade 585 · admin 50 · tribute 375 · upkeep 272 · charges 584
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 20).
  - TURN EVENTS 8
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Munich. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mov…
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Munich. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 2 actions unused) Turn 32 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 53785 · net +3092 · threat 26 · provinces 25 (+0) · ceiling 311416 · army 37607 · vassals Holland 91 · Kingdom of Italy 100 · Switzerland 77
  - NET income 2900 · trade 585 · admin 50 · tribute 450 · upkeep 272 · charges 621
- DISPATCH: Ney's fortifications strengthen: +7% defense (max 8%)
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Munich. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 actions unused) Turn 33 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 56885 · net +3288 · threat 23 · provinces 25 (+0) · ceiling 330833 · army 37031 · vassals Holland 90 · Kingdom of Italy 100 · Switzerland 76
  - NET income 2900 · trade 585 · admin 50 · tribute 675 · upkeep 264 · charges 658
- DISPATCH: DRILL COMPLETE: Lannes's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 51).
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 33 — Late January 1807
  - MAILBOX #16 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #22 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (600g forgone). Loyalty +10 (90 → 100); bond 25 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Munich. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Munich. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cann…
- CMD `Soult, unfortify` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 5,000 cavalry at Paris (recruitment is drafted in fixed corps of 5,000, Sire — your 10,000 is note…
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 2 actions unused) Turn 34 begins!
- SPENT 259g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 59777 · net +3138 · threat 20 · provinces 25 (+0) · ceiling 321250 · army 41473 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 75
  - NET income 2900 · trade 585 · admin 50 · tribute 600 · upkeep 304 · charges 693
- DISPATCH: Davout is now locked in intensive drill. Cannot receive orders until training completes.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 34 — Early February 1807
  - MAILBOX #17 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #23 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (75 → 85); bond 25 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Munich. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 actions unused) Turn 35 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 62690 · net +2878 · threat 17 · provinces 25 (+0) · ceiling 302500 · army 40932 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 85
  - NET income 2900 · trade 585 · admin 50 · tribute 375 · upkeep 304 · charges 728
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Munich. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Munich. Army is now mobile.
- CMD `Soult, drill` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 2 actions unused) Turn 36 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 65568 · net +2844 · threat 14 · provinces 25 (+0) · ceiling 302500 · army 40407 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 85
  - NET income 2900 · trade 585 · admin 50 · tribute 375 · upkeep 304 · charges 762
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 30).
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sweden (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Munich. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mov…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier checks the order of battle. 'No marshal of infantry can reach Paris, Sire — Murat commands cavalry.' Bernadotte commands our foot at Nivernais — march him withi…
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 2 actions unused) Turn 37 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 68420 · net +2817 · threat 11 · provinces 25 (+0) · ceiling 303166 · army 39897 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 85
  - NET income 2900 · trade 585 · admin 50 · tribute 375 · upkeep 296 · charges 797
- DISPATCH: Ney's fortifications have crumbled completely!
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Munich. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 3 actions unused) Turn 38 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 71245 · net +2792 · threat 8 · provinces 25 (+0) · ceiling 303833 · army 39402 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 85
  - NET income 2900 · trade 585 · admin 50 · tribute 375 · upkeep 288 · charges 830
- DISPATCH: Ney's fortifications strengthen: +2% defense (max 8%)
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Munich. Army is now mobile.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 3 actions unused) Turn 39 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 74037 · net +2758 · threat 5 · provinces 25 (+0) · ceiling 303833 · army 38923 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 85
  - NET income 2900 · trade 585 · admin 50 · tribute 375 · upkeep 288 · charges 864
- DISPATCH: DRILL COMPLETE: Lannes's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 61).
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Munich. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Munich, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 3 actions unused) Turn 40 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 76753 · net +2683 · threat 2 · provinces 25 (+0) · ceiling 300333 · army 38458 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 85
  - NET income 2900 · trade 535 · admin 50 · tribute 375 · upkeep 280 · charges 897
- DISPATCH: Davout is now locked in intensive drill. Cannot receive orders until training completes.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Bavaria–France (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Munich. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Milan (+2% defense).
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 actions unused) Turn 41 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 79444 · net +2734 · threat 0 · provinces 25 (+0) · ceiling 307250 · army 38007 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 85
  - NET income 2900 · trade 535 · admin 50 · tribute 450 · upkeep 272 · charges 929
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (500g/turn)

---
finished: **completed** · commands 200 · popups 53 · battles 29
