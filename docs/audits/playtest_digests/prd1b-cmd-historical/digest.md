# Playtest digest — prd1b-cmd-historical

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `759414f922cb` (dirty) · content `f797f1101c51` · driver `196c4ee545c1`
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
  - RAIL peace_ratified: Peace ratified between Austria and France.
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
  - POPUP diplomatic_dialogue: force_declare_war_confirmation #16 → reconsider
- CMD `Davout, move to Franconia` → ✓ Davout moves from Swabia to Franconia (105 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 2 actions unused) Turn 14 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, garrison×1, wait×1
- LEDGER treasury 33603 · net +3373 · threat 39 · provinces 28 (+0) · ceiling 314666 · army 90973 · vassals Holland 96 · Kingdom of Italy 97 · Switzerland 83
  - NET income 3400 · trade 623 · admin 50 · tribute 375 · upkeep 696 · charges 379
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 10).
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 14 — Early April 1806
- CMD `Lannes, fortify` → ✗ Lannes is already fortified at Swabia (+2% defense).
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Fra…
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Milan and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 2 actions unused) Turn 15 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, recruit×1, wait×1
- LEDGER treasury 36976 · net +3558 · threat 39 · provinces 28 (+0) · ceiling 333416 · army 89136 · vassals Holland 95 · Kingdom of Italy 98 · Switzerland 82
  - NET income 3400 · trade 623 · admin 50 · tribute 600 · upkeep 696 · charges 419
- DISPATCH: Sire — Davout, Murat and Ney are no nearer home, and the safe passage runs out in 2 turns. After that their corps will be interned where they stand.
  - TURN EVENTS 7
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)

## Turn 15 — Late April 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1, wait×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 40566 · net +3547 · threat 39 · provinces 28 (+0) · ceiling 336083 · army 87360 · vassals Holland 94 · Kingdom of Italy 99 · Switzerland 81
  - NET income 3400 · trade 623 · admin 50 · tribute 600 · upkeep 664 · charges 462
- DISPATCH: Sire — Davout, Murat, Ney, Lannes and Soult are no nearer home, and the safe passage runs out in 1 turn. After that their corps will be interned where they stand.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 16 — Early May 1806
  - MAILBOX #13 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #17 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (81 → 91); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, move to Bohemia` → ✗ Cannot enter Bohemia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action unused) Turn 17 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 43904 · net +3298 · threat 39 · provinces 28 (+0) · ceiling 318666 · army 85642 · vassals Holland 93 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 623 · admin 50 · tribute 375 · upkeep 648 · charges 502
- DISPATCH: Sire — Davout, Murat, Ney, Lannes and Soult are no nearer home, and the safe passage runs out in 0 turns. After that their corps will be interned where they stand.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Milan (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action unused) Turn 18 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, wait×1
- LEDGER treasury 47218 · net +3538 · threat 39 · provinces 28 (+0) · ceiling 342000 · army 49695 · vassals Holland 92 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 623 · admin 50 · tribute 375 · upkeep 368 · charges 542
- DISPATCH: Sire — Marshal Ney's corps was interned at Franconia by Austria — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✗ Marshal Murat is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier checks the order of battle. 'No marshal of infantry can reach Paris, Sire — none of ours stands within reach.' Massena commands our foot at Milan — march him wi…
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 50756 · net +4048 · threat 39 · provinces 28 (+0) · ceiling 388083 · army 21063 · vassals Holland 91 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 623 · admin 50 · tribute 712 · upkeep 152 · charges 585
- DISPATCH: Sire — Marshal Davout's corps was interned at Franconia by Austria — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Davout, unfortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, move to Franconia` → ✗ Marshal Lannes is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Murat, drill` → ✗ Marshal Murat is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission…
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 54804 · net +4000 · threat 37 · provinces 28 (+0) · ceiling 388083 · army 20871 · vassals Holland 90 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 623 · admin 50 · tribute 712 · upkeep 152 · charges 633
- DISPATCH: Sire — Marshal Soult's corps was interned at Swabia by Austria — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 9 courts rebuff Austria (defensive alliance)

## Turn 20 — Early July 1806
  - MAILBOX #14 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #18 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (90 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Soult, fortify` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 58467 · net +3619 · threat 35 · provinces 28 (+0) · ceiling 360000 · army 20684 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 623 · admin 50 · tribute 375 · upkeep 152 · charges 677
- DISPATCH: Massena's fortifications strengthen: +2% defense (max 8%)
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Davout, drill` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, fortify` → ✗ Marshal Lannes is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier checks the order of battle. 'No marshal of infantry can reach Paris, Sire — none of ours stands within reach.' Massena commands our foot at Milan — march him wi…
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 4 actions unused) Turn 22 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 62086 · net +3575 · threat 33 · provinces 28 (+0) · ceiling 360000 · army 20500 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 623 · admin 50 · tribute 375 · upkeep 152 · charges 721
- DISPATCH: Massena's fortifications have crumbled completely!
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- COURTS: The court of Sweden eases over Scourge of the Usurper — service to the strong is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `Murat, fortify` → ✗ Marshal Murat is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission…
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 3 actions unused) Turn 23 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 65661 · net +3533 · threat 31 · provinces 28 (+0) · ceiling 360000 · army 20320 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 623 · admin 50 · tribute 375 · upkeep 152 · charges 763
- DISPATCH: Supply cost you 180 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Davout, fortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, unfortify` → ✗ Marshal Lannes is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Soult, drill` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 4 actions unused) Turn 24 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 69194 · net +3715 · threat 29 · provinces 28 (+0) · ceiling 378750 · army 20143 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 623 · admin 50 · tribute 600 · upkeep 152 · charges 806
- DISPATCH: Supply cost you 177 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Marshal Murat is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier checks the order of battle. 'No marshal of infantry can reach Paris, Sire — none of ours stands within reach.' Massena commands our foot at Milan — march him wi…
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 actions unused) Turn 25 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: defend×1
- LEDGER treasury 72909 · net +3671 · threat 27 · provinces 28 (+0) · ceiling 378750 · army 19971 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 623 · admin 50 · tribute 600 · upkeep 152 · charges 850
- DISPATCH: Massena's fortifications have crumbled completely!
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sweden and Austria (Defensive Alliance)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Davout, unfortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, drill` → ✗ Marshal Lannes is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Soult, fortify` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 4 actions unused) Turn 26 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 76580 · net +3627 · threat 25 · provinces 28 (+0) · ceiling 378750 · army 19802 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 623 · admin 50 · tribute 600 · upkeep 152 · charges 894
- DISPATCH: Massena's fortifications strengthen: +2% defense (max 8%)
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Marshal Murat is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission…
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 80215 · net +3591 · threat 23 · provinces 28 (+0) · ceiling 379416 · army 19636 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 623 · admin 50 · tribute 600 · upkeep 144 · charges 938
- DISPATCH: Massena's fortifications have crumbled completely!
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, fortify` → ✗ Marshal Lannes is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Soult, unfortify` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier checks the order of battle. 'No marshal of infantry can reach Paris, Sire — none of ours stands within reach.' Massena commands our foot at Milan — march him wi…
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 4 actions unused) Turn 28 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 83806 · net +3885 · threat 21 · provinces 28 (+0) · ceiling 407500 · army 19474 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 623 · admin 50 · tribute 937 · upkeep 144 · charges 981
- DISPATCH: Massena's fortifications strengthen: +2% defense (max 8%)
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Murat, fortify` → ✗ Marshal Murat is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission…
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Sweden defensive alliance
- LEDGER treasury 87691 · net +3838 · threat 19 · provinces 28 (+0) · ceiling 407500 · army 19315 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 623 · admin 50 · tribute 937 · upkeep 144 · charges 1028
- DISPATCH: Supply cost you 159 men, at Franche-Comte.
  - RAIL diplomatic_ai_proposal: An envoy from Sweden has arrived with a proposal.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 29 — Late November 1806
  - MAILBOX #15 Sweden incoming_proposal: Sweden — Defensive Alliance → activated
  - POPUP diplomatic_dialogue: Sweden, defensive_alliance #19 → accept
  -     ↳ refused: Sweden's terms could not be ratified: Relations with France are insufficient for DEFENSIVE_ALLIANCE.
- CMD `Davout, fortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, unfortify` → ✗ Marshal Lannes is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Soult, drill` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `Ney, drill` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 4 actions unused) Turn 30 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 91529 · net +3792 · threat 17 · provinces 28 (+0) · ceiling 407500 · army 19159 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 623 · admin 50 · tribute 937 · upkeep 144 · charges 1074
- DISPATCH: Supply cost you 156 men, at Franche-Comte.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)
  - LOG ai_proposal_rejected: We rejected Sweden's defensive alliance proposal

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Marshal Murat is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier checks the order of battle. 'No marshal of infantry can reach Paris, Sire — none of ours stands within reach.' Massena commands our foot at Milan — march him wi…
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 95329 · net +3755 · threat 15 · provinces 28 (+0) · ceiling 408166 · army 19006 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 623 · admin 50 · tribute 937 · upkeep 136 · charges 1119
- DISPATCH: Massena's fortifications have crumbled completely!
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Davout, unfortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, drill` → ✗ Marshal Lannes is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Soult, fortify` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 4 actions unused) Turn 32 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 99084 · net +3709 · threat 13 · provinces 28 (+0) · ceiling 408166 · army 18856 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 623 · admin 50 · tribute 937 · upkeep 136 · charges 1165
- DISPATCH: Massena's fortifications strengthen: +2% defense (max 8%)
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Marshal Murat is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission…
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Sweden defensive alliance
- LEDGER treasury 102793 · net +3665 · threat 11 · provinces 28 (+0) · ceiling 408166 · army 18709 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 623 · admin 50 · tribute 937 · upkeep 136 · charges 1209
- DISPATCH: Massena's fortifications have crumbled completely!
  - RAIL diplomatic_ai_proposal: An envoy from Sweden has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 33 — Late January 1807
  - MAILBOX #16 Sweden incoming_proposal: Sweden — Defensive Alliance → activated
  - POPUP diplomatic_dialogue: Sweden, defensive_alliance #20 → accept
  -     ↳ refused: Sweden's terms could not be ratified: Relations with France are insufficient for DEFENSIVE_ALLIANCE.
- CMD `Davout, drill` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, fortify` → ✗ Marshal Lannes is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Soult, unfortify` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier checks the order of battle. 'No marshal of infantry can reach Paris, Sire — none of ours stands within reach.' Massena commands our foot at Milan — march him wi…
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 4 actions unused) Turn 34 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 106458 · net +3621 · threat 9 · provinces 28 (+0) · ceiling 408166 · army 18565 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 623 · admin 50 · tribute 937 · upkeep 136 · charges 1253
- DISPATCH: Massena's fortifications strengthen: +2% defense (max 8%)
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Sweden's defensive alliance proposal

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Marshal Murat is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission…
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `Ney, drill` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 3 actions unused) Turn 35 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 110041 · net +3540 · threat 7 · provinces 28 (+0) · ceiling 405000 · army 18424 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 585 · admin 50 · tribute 937 · upkeep 136 · charges 1296
- DISPATCH: Supply cost you 141 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, unfortify` → ✗ Marshal Lannes is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Soult, drill` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `Murat, drill` → ✗ Marshal Murat is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission…
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 4 actions unused) Turn 36 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 113581 · net +3498 · threat 5 · provinces 28 (+0) · ceiling 405000 · army 18286 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 585 · admin 50 · tribute 937 · upkeep 136 · charges 1338
- DISPATCH: Supply cost you 138 men, at Franche-Comte.
  - TURN EVENTS 1
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier checks the order of battle. 'No marshal of infantry can reach Paris, Sire — none of ours stands within reach.' Massena commands our foot at Milan — march him wi…
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 3 actions unused) Turn 37 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Sweden defensive alliance
- LEDGER treasury 117079 · net +3456 · threat 3 · provinces 28 (+0) · ceiling 405000 · army 18150 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 585 · admin 50 · tribute 937 · upkeep 136 · charges 1380
- DISPATCH: Massena's fortifications have crumbled completely!
  - RAIL diplomatic_ai_proposal: An envoy from Sweden has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (defensive alliance)

## Turn 37 — Late March 1807
  - MAILBOX #17 Sweden incoming_proposal: Sweden — Defensive Alliance → activated
  - POPUP diplomatic_dialogue: Sweden, defensive_alliance #21 → accept
  -     ↳ refused: Sweden's terms could not be ratified: Relations with France are insufficient for DEFENSIVE_ALLIANCE.
- CMD `Davout, unfortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, drill` → ✗ Marshal Lannes is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Soult, fortify` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `Murat, unfortify` → ✗ Marshal Murat is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission…
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 4 actions unused) Turn 38 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 120543 · net +3422 · threat 1 · provinces 28 (+0) · ceiling 405666 · army 18017 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 585 · admin 50 · tribute 937 · upkeep 128 · charges 1422
- DISPATCH: Massena's fortifications strengthen: +2% defense (max 8%)
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Sweden's defensive alliance proposal

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Marshal Lannes is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 123965 · net +3381 · threat 0 · provinces 28 (+0) · ceiling 405666 · army 17887 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 585 · admin 50 · tribute 937 · upkeep 128 · charges 1463
- DISPATCH: Massena's fortifications have crumbled completely!
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Soult, unfortify` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `Murat, fortify` → ✗ Marshal Murat is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier checks the order of battle. 'No marshal of infantry can reach Paris, Sire — none of ours stands within reach.' Massena commands our foot at Milan — march him wi…
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 4 actions unused) Turn 40 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 127346 · net +3340 · threat 0 · provinces 28 (+0) · ceiling 405666 · army 17759 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 585 · admin 50 · tribute 937 · upkeep 128 · charges 1504
- DISPATCH: Massena's fortifications strengthen: +2% defense (max 8%)
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Massena, fortify` → ✗ Massena is already fortified at Milan (+2% defense).
- CMD `Davout, fortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 actions unused) Turn 41 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Sweden defensive alliance
- LEDGER treasury 130686 · net +3300 · threat 0 · provinces 28 (+0) · ceiling 405666 · army 17634 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 91
  - NET income 3400 · trade 585 · admin 50 · tribute 937 · upkeep 128 · charges 1544
- DISPATCH: Massena's fortifications have crumbled completely!
  - RAIL diplomatic_ai_proposal: An envoy from Sweden has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (500g/turn)

---
finished: **completed** · commands 200 · popups 42 · battles 18
