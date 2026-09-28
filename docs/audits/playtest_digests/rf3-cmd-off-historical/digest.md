# Playtest digest — rf3-cmd-off-historical

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `3d1157842721` (dirty) · content `c696461ccc07` · driver `aef52ad7cbfd`
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
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
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
  - ⚔ Ney (lost 657, own corps) vs Mack (lost 21150) — Davout and Massena arrived to reinforce Ney, but Napoleon failed to reach the field in time.
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (22,793; expect about 33,156 with the corps likely to arrive, up to 44,815 if all march) vs Mack (large force) at Tyrol — the balance of force looks even…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 8051) vs Archduke Charles (lost 1190, own corps) — Davout stood alone, Sire. Ney never came.
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✗ Murat is already in Franche-Comte.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 2 actions unused) Turn 3 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · Deroy launches a decisive assault. ArchdukeJohn holds the line. Casualties: Deroy 3,394, ArchdukeJohn 1,572. Both armie… · Deroy engages in solid combat. ArchdukeJohn holds the line. Casualties: Deroy 3,180, ArchdukeJohn 1,146. Both armies re…
  - ⚔ Archduke Charles (lost 1879) vs Bernadotte (lost 5468) — Bernadotte stood alone, Sire. Ney never came.
  - ⚔ Deroy (lost 3394) vs Archduke John (lost 1572) — Archduke John's fortifications held firm, Sire. Deroy broke against our walls.
  - ⚔ Deroy (lost 3180) vs Archduke John (lost 1146) — The prepared defenses proved their worth. Deroy could not dislodge Archduke John.
  - verbs: attack×3, fortify×1, wait×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 4494 · net +2636 · threat 82 · provinces 28 (+0) · ceiling 49931 · army 159038 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 94
  - NET income 3400 · trade 450 · admin 50 · tribute 901 · upkeep 1706 · charges 144 · blockade 225 · admiralty 90
- DISPATCH: Sire — Davout's corps has been broken at Munich. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +7 medium/low (diplomatic_treaty_signed ×3, diplomatic_we_threshold ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 26 approaches from Prussia, Bavaria and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (19,912; expect about 52,610 with the corps likely to arrive, up to 53,910 if all march) vs Mack (13,746 men) at Tyrol — the balance of force looks favorabl…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 499, own corps) vs Mack (lost 7234, own corps) — Massena's timely arrival bolstered Ney's position. Well-coordinated, Sire.
  - POPUP capture_choice[capture]: Tyrol, Ney → secure
- CMD `Davout, attack Mack` → ✗ Davout is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Rhineland to Swabia (166 lost to march)
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 711 gold (×3 at war) (×1.19 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 2 actions unused) Turn 4 begins!
- SPENT 711g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 6426 · net +2414 · threat 90 · provinces 29 (+1) · ceiling 32775 · army 158946 · vassals Holland 98 · Kingdom of Italy 98 · Switzerland 93
  - NET income 3420 · trade 525 · admin 50 · tribute 905 · upkeep 1676 · charges 405 · occupation 52 · blockade 263 · admiralty 90
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
  - ⚔ Archduke Charles (lost 1468) vs Deroy (lost 5213) — The hills were ours, but Archduke Charles took them. Deroy's position was overrun.
  - verbs: attack×2, fortify×1, stance_change×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 9000 · net +2235 · threat 88 · provinces 29 (+0) · ceiling 32569 · army 157081 · vassals Holland 98 · Kingdom of Italy 98 · Switzerland 91
  - NET income 3421 · trade 587 · admin 50 · tribute 910 · upkeep 1634 · charges 663 · occupation 52 · blockade 294 · admiralty 90
- DISPATCH: Sire — Bohemia has been taken by Austria.
  - TURN EVENTS 7
- DIPLO +3 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Denmark rebuffs Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 2 more — Bavaria is not forgiven
  - LOG ai_ai_proposal_refused: 28 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)

## Turn 5 — Late November 1805
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (17,948) vs Archduke Charles (38,166 men) at Carniola — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1891, own corps) vs Archduke Charles (lost 1678) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
- CMD `Lannes, attack Mack` → ✗ No intelligence on Mack's position, Sire. Scout for him before Lannes can give chase.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (990 lost to march)
- CMD `Murat, move to Swabia` → ✓ Murat moves from Franche-Comte to Swabia (308 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 1 action unused) Turn 6 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, wait×1, recruit×1
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 11552 · net +2611 · threat 86 · provinces 29 (+0) · ceiling 47218 · army 146939 · vassals Holland 96 · Kingdom of Italy 96 · Switzerland 87
  - NET income 3465 · trade 587 · admin 50 · tribute 914 · upkeep 1292 · charges 699 · occupation 30 · blockade 294 · admiralty 90
- DISPATCH: Sire — Ney, crowned four turns ago, has been beaten in the field.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria

## Turn 6 — Early December 1805
  - MAILBOX #8 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #9 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to the Kingdom of Italy. Loyalty +4 (96 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. Our net rises by 6g a turn — 65g of income forfeited, 30g of occupation relieved, 49g returned as tribute at today's 75% rate, the force limit falls 2,500 (+8g surcharge). → display-only
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! ArchdukeCharles is at Carniola, just one region away.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 2 actions unused) Turn 7 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn's forces press forward aggressively. Ney holds the line. Casualties: ArchdukeJohn 4,879, Ney's army 1,046.…
  - ⚔ Archduke John (lost 4879) vs Ney (lost 373, own corps) — A decisive victory for Ney! Archduke John was thoroughly outmatched.
  - verbs: attack×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
  -     ↳ Massena's grievance runs its course.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #10 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (86 → 96); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 14161 · net +2232 · threat 84 · provinces 28 (-1) · ceiling 43210 · army 142573 · vassals Holland 97 · Kingdom of Italy 100 · Switzerland 96
  - NET income 3400 · trade 587 · admin 50 · tribute 708 · upkeep 1196 · charges 933 · blockade 294 · admiralty 90
- DISPATCH: Sire — Leon has been taken by Britain.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 7 — Late December 1805
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (15,148) vs Archduke Charles (36,488 men) at Carniola — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2107, own corps) vs Archduke Charles (lost 750) — Massena marched to Ney's guns as ordered. It was not enough.
- CMD `Davout, move to Bohemia` → ✓ Davout begins marching to Bohemia (distance: 3). Moved to Swabia. Route: Swabia -> Franconia -> Bohemia.
- CMD `Murat, attack Archduke Charles` → ✗ Not enough actions for a strategic pursuit! Need 2, have 1.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 1 action unused) Turn 8 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Bernadotte. Casualties: A…
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Tyrol. (2,111 lost to march) Tyrol has been captured by Austria!
  - ⚔ Archduke Charles (lost 550) vs Massena (lost 10874) — Massena stood alone, Sire. Bernadotte never came.
  - ⚔ Archduke Charles (lost 719) vs Bernadotte (lost 6109) — Where was Soult? Bernadotte held the field alone — reinforcement never came.
  - verbs: attack×2, unfortify×1, wait×1
- ORDER Davout [active]: Davout is marching to Bohemia (3 turns remaining).
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Austria, armistice_losing #11 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 15391 · net +2135 · threat 82 · provinces 28 (+0) · ceiling 36651 · army 112837 · vassals Holland 91 · Kingdom of Italy 95 · Switzerland 89
  - NET income 3400 · trade 587 · admin 50 · tribute 698 · upkeep 872 · charges 1344 · blockade 294 · admiralty 90
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
- enemy phase: 6 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Franconia where he stands! (917 lost to march) Captured: Bavaria → Austria · ArchdukeCharles's forces advance steadily. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCharles …
  - 🏴 Austria: ArchdukeCharles takes Franconia where he stands! (917 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Munich. (1,474 lost to march) Munich has been captured by Austria!
  - ⚔ Archduke Charles (lost 1538) vs Deroy (lost 3938) — Deroy held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: attack×2, move×1, garrison×1, wait×1, recruit×1
- ORDER Massena [active]: Massena is marching to Milan (2 turns remaining).
- LEDGER treasury 17544 · net +1930 · threat 80 · provinces 28 (+0) · ceiling 36169 · army 107098 · vassals Holland 91 · Kingdom of Italy 94 · Switzerland 88
  - NET income 3400 · trade 587 · admin 50 · tribute 703 · upkeep 816 · charges 1610 · blockade 294 · admiralty 90
- DISPATCH: Sire — Franconia has been taken by Austria.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 6
- COURTS: The court of Austria eases over Redeem Italy — an ultimatum is now the length of its tether.
- DIPLO +4 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 10 approaches from Austria and Prussia are rebuffed (defensive alliance)

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Lannes, move to Bohemia` → ✗ Lannes is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 11.
- CMD `recruit 10000 cavalry with Murat` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 actions unused) Turn 10 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. ArchdukeCharles gains the advantage over Deroy. Casualties: Archdu… · Castanos engages in solid combat. Castanos gains the advantage over Paget. Casualties: Castanos 654, Paget 1,649. Both … · Castanos holds them at Leon while allies attack from Aragon! (+1 coordination)
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Swabia. (557 lost to march) Swabia has been captured by Austria!
  - 🏴 Spain: [!] Paget's troops are BROKEN (morale 0%)! FORCED RETREAT! Leon has been captured by Spain!
  - ⚔ Archduke Charles (lost 558) vs Deroy (lost 9288) — A grievous defeat for Deroy, Sire. The losses are severe.
  - ⚔ Castanos (lost 654) vs Paget (lost 1649) — An aggressive stance invites disaster when one is not the attacker, Sire. Paget paid the price.
  - ⚔ Castanos (lost 392) vs Paget (lost 1789) — Paget's aggressive posture left the troops exposed when Castanos's attack came. And Paget was taken on that field — Spa…
  - verbs: attack×3, fortify×1, move×1
- ORDER Massena [completed]: Massena arrives at Milan. Massena: "It is done. Point me at something that shoots back, Sire."
- ORDER Ney [continues]: Ney marches to Swabia. 1 region to Rhineland.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Ney: They settle into cold war.
  - POPUP diplomatic_dialogue: incoming_settlement_offer #12 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #13 → seek_bilateral_peace
  - POPUP diplomatic_dialogue: settlement_pair_substitute_confirm, peace #14 → confirm_pair_substitute
  - POPUP diplomatic_dialogue: proposal_confirm #15 → (left standing — disabled: I cannot deliver this, Sire — Making peace with Britain while allied with Spain (who is s…)
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 19437 · net +1691 · threat 78 · provinces 28 (+0) · ceiling 35267 · army 101123 · vassals Holland 91 · Kingdom of Italy 95 · Switzerland 87
  - NET income 3400 · trade 524 · admin 50 · tribute 707 · upkeep 776 · charges 1862 · blockade 262 · admiralty 90
- DISPATCH: Sire — Ney, Davout, Soult, Lannes, Murat, Bernadotte and Napoleon have been 4 turns over what Swabia can feed. 16,516 men. The country will ask where the army went. No depot may be laid at Swabia — n…
  - RAIL nation_eliminated: Bavaria has been eliminated from the war.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 9
- DIPLO +2 medium/low (diplomatic_we_threshold, diplomatic_dp_regen)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG ai_ai_proposal_refused: 17 approaches rebuffed, chiefly from Prussia and Austria (open borders agreement)

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney moves from Swabia to Franconia (118 lost to march)
- CMD `Davout, fortify` → ✓ Davout fortifies position at Swabia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Soult, move to Bavaria` → ✗ Region 'Bavaria' not found. Did you mean 'Balearics'?
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 actions unused) Turn 11 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- ORDER Bernadotte [completed]: Bernadotte arrives at Franche-Comte. Bernadotte: "Accomplished as ordered. The army is intact."
- ORDER Lannes [error]: Lannes could not advance toward Franche-Comte.
- ORDER Murat [error]: Murat could not advance toward Franche-Comte.
- ORDER Napoleon [completed]: Napoleon arrives at Franche-Comte.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Bernadotte and Ney: They settle into cold war.
- LEDGER treasury 21101 · net +1481 · threat 76 · provinces 28 (+0) · ceiling 34563 · army 97090 · vassals Holland 91 · Kingdom of Italy 96 · Switzerland 86
  - NET income 3400 · trade 524 · admin 50 · tribute 712 · upkeep 752 · charges 2101 · blockade 262 · admiralty 90
- DISPATCH: Sire — Ney is no nearer home, and the safe passage runs out in 2 turns. After that his corps will be interned where it stands.
  - TURN EVENTS 8
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG nation_eliminated: Bavaria has been eliminated from the war.
  - LOG ai_ai_proposal_refused: 10 approaches rebuffed, chiefly from Prussia (open borders agreement)

## Turn 11 — Late February 1806
- CMD `Ney, attack Archduke John` → ✗ Cannot attack ArchdukeJohn — armistice with Austria (2 turns remaining).
- CMD `Lannes, attack Archduke John` → ✗ Lannes is fortified at Swabia and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Swabia to Franconia (158 lost to march)
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 1 action unused) Turn 12 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Naples open borders
- LEDGER treasury 22545 · net +1281 · threat 74 · provinces 28 (+0) · ceiling 33855 · army 95014 · vassals Holland 91 · Kingdom of Italy 97 · Switzerland 85
  - NET income 3400 · trade 524 · admin 50 · tribute 712 · upkeep 728 · charges 2325 · blockade 262 · admiralty 90
- DISPATCH: Sire — Murat, Ney, Davout, Lannes and Soult are no nearer home, and the safe passage runs out in 1 turn. After that their corps will be interned where they stand.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)

## Turn 12 — Early March 1806
  - LETTER Naples: Open Borders Agreement → accept
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, unfortify×1
- LEDGER treasury 24000 · net +1153 · threat 72 · provinces 28 (+0) · ceiling 33898 · army 93118 · vassals Holland 91 · Kingdom of Italy 98 · Switzerland 84
  - NET income 3400 · trade 549 · admin 50 · tribute 712 · upkeep 720 · charges 2560 · requisitions 87 · blockade 275 · admiralty 90
- DISPATCH: Sire — Davout, Soult and Lannes have been 7 turns over what Swabia can feed. 7,729 men. The country will ask where the army went. No depot may be laid at Swabia — not controlled by France. Rhineland …
  - RAIL diplomatic_armistice_expired_war: The armistice between Austria and France has collapsed. War resumes!
  - TURN EVENTS 7
- COURTS: The court of Austria hardens over Redeem Italy — prepared now to go as far as war.
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✗ Cannot charge through Bohemia - Mack blocks the path! Engage them first.
- CMD `Davout, move to Franconia` → ✗ Cannot advance while engaged with enemy forces. You may retreat to friendly territory.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: 6 actions, 2 attacks — Britain, Russia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Mack struggles in a costly engagement. Mack gains the advantage over Ney. Casualties: Mack 1,335, Ney's army 5,024. Bot… · Mack holds them at Franconia while allies attack from Bohemia! (+1 coordination)
  - ⚔ Mack (lost 1335) vs Ney (lost 2650, own corps) — Davout marched to Ney's guns as ordered. It was not enough.
  - ⚔ Mack (lost 1988, own corps) vs Murat (lost 3101) — An inconclusive affair. Both sides bloodied but unbroken.
  - verbs: attack×2, retreat×1, stance_change×1, recruit×1, wait×1
- LEDGER treasury 24659 · net +930 · threat 70 · provinces 28 (+0) · ceiling 32039 · army 84441 · vassals Holland 89 · Kingdom of Italy 99 · Switzerland 81
  - NET income 3400 · trade 549 · admin 50 · tribute 712 · upkeep 648 · charges 2855 · requisitions 87 · blockade 275 · admiralty 90
- DISPATCH: Sire — Ney's corps has been broken at Franconia. He must reform before he fights again.
  - TURN EVENTS 9
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 14 — Early April 1806
- CMD `Lannes, fortify` → ✗ Lannes is already fortified at Swabia (+2% defense).
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is recovering from retreat and cannot fortify. Recovery: 2 turns remaining.
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Milan and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 4 actions unused) Turn 15 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — Mack engages in solid combat. Brutal stalemate between Mack and Murat. Heavy casualties on both sides: Mack's army 2,39…
  - ⚔ Mack (lost 1645, own corps) vs Murat (lost 3251) — Neither Murat nor Mack could claim the field. The armies remain locked.
  - verbs: attack×1, move×1, wait×1, fortify×1, recruit×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 25355 · net +970 · threat 68 · provinces 28 (+0) · ceiling 32746 · army 80714 · vassals Holland 89 · Kingdom of Italy 100 · Switzerland 80
  - NET income 3400 · trade 549 · admin 50 · tribute 937 · upkeep 624 · charges 3064 · requisitions 87 · blockade 275 · admiralty 90
- DISPATCH: Sire — Murat was mauled at Franconia: a quarter of his corps — 3,251 men — lost in a single action.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 15 — Late April 1806
  - MAILBOX #13 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #17 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #18 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain + Russia (6 pairs resolved). → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Berlin. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 3 actions unused) Turn 16 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1
- ORDER Lannes [error]: Lannes could not advance toward Franche-Comte.
- ORDER Murat [completed]: Murat arrives at Rhineland. Murat: "Done — and I trust the next order has more fire in it."
- ORDER Soult [error]: Soult could not advance toward Franche-Comte.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 29423 · net +4019 · threat 34 · provinces 28 (+0) · ceiling 364333 · army 80168 · vassals Holland 87 · Kingdom of Italy 100 · Switzerland 79
  - NET income 3400 · trade 585 · admin 50 · tribute 937 · upkeep 624 · charges 329
- DISPATCH: Sire — the war with Austria is over. 3 corps stand on the wrong side of the new frontier. Berthier has given them the road home — Soult to Franche-Comte, Lannes to Franche-Comte, Murat to Rhineland. …
  - RAIL settlement_summary: Settlement of France + Spain + Holland + Kingdom of Italy vs Britain + Austria + Russia: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 7
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: And 3 other courts stir at their own designs.
- DIPLO +5 medium/low (diplomatic_coalition_dissolved, diplomatic_dp_regen, blockade_broken ×3)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 68 to 34.

## Turn 16 — Early May 1806
  - MAILBOX #14 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #19 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (87 → 97); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Ney, move to Bohemia` → ✗ Cannot enter Bohemia — the evacuation corridor with Austria grants safe passage HOME to stranded corps, not entry. Ney can already reach the body of the realm from where…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action unused) Turn 17 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- ORDER Lannes [completed]: Lannes arrives at Franche-Comte. Lannes: "Done — and I trust the next order has more fire in it."
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 33121 · net +3654 · threat 34 · provinces 28 (+0) · ceiling 337583 · army 79287 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 78
  - NET income 3400 · trade 585 · admin 50 · tribute 600 · upkeep 608 · charges 373
- DISPATCH: Sire — Soult is no nearer home, and the safe passage runs out in 2 turns. After that his corps will be interned where it stands.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 17 — Late May 1806
  - MAILBOX #15 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #20 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (78 → 88); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Ber…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Berlin. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Not enough actions! Need 1, have 0.
- CMD `end turn` → ✓ Turn 17 ended. Turn 18 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- LEDGER treasury 36558 · net +3396 · threat 34 · provinces 28 (+0) · ceiling 319500 · army 78433 · vassals Holland 95 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3400 · trade 585 · admin 50 · tribute 375 · upkeep 600 · charges 414
- DISPATCH: Sire — Soult is no nearer home, and the safe passage runs out in 1 turn. After that his corps will be interned where it stands.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Rhineland. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Berlin, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, unfortify×1
- LEDGER treasury 39962 · net +3363 · threat 34 · provinces 28 (+0) · ceiling 320166 · army 77607 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3400 · trade 585 · admin 50 · tribute 375 · upkeep 592 · charges 455
- DISPATCH: Sire — Soult is no nearer home, and the safe passage runs out in 0 turns. After that his corps will be interned where it stands.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Berlin. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✗ Cannot enter Franconia — the evacuation corridor with Austria grants safe passage HOME to stranded corps, not entry. Lannes can already reach the body of the realm from …
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 3 actions unused) Turn 20 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1, wait×1
- LEDGER treasury 43325 · net +3491 · threat 34 · provinces 28 (+0) · ceiling 334166 · army 55343 · vassals Holland 93 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3400 · trade 585 · admin 50 · tribute 375 · upkeep 424 · charges 495
- DISPATCH: Sire — Marshal Soult's corps was interned at Swabia by Austria — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Berlin. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 actions unused) Turn 21 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, fortify×1
- LEDGER treasury 46824 · net +3457 · threat 34 · provinces 28 (+0) · ceiling 334833 · army 54567 · vassals Holland 92 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3400 · trade 585 · admin 50 · tribute 375 · upkeep 416 · charges 537
- DISPATCH: Sire — Marshal Soult's corps was interned at Swabia by Austria — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Berlin. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franche-Comte. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only…
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Rhineland (field levy — no depot; capped at 3,000) (recruitment is drafted in fix…
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 actions unused) Turn 22 begins!
- SPENT 345g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1
- LEDGER treasury 49899 · net +3404 · threat 34 · provinces 28 (+0) · ceiling 333500 · army 56814 · vassals Holland 91 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3400 · trade 585 · admin 50 · tribute 375 · upkeep 432 · charges 574
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 10).
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- COURTS: The court of Sweden eases over Scourge of the Usurper — service to the strong is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 3 actions unused) Turn 23 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 53311 · net +3371 · threat 34 · provinces 28 (+0) · ceiling 334166 · army 56084 · vassals Holland 90 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3400 · trade 585 · admin 50 · tribute 375 · upkeep 424 · charges 615
- DISPATCH: DRILL COMPLETE: Davout's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 20).
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Berlin. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Soult, drill` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 2 actions unused) Turn 24 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, fortify×1
- LEDGER treasury 56698 · net +3683 · threat 34 · provinces 28 (+0) · ceiling 363583 · army 55336 · vassals Holland 89 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3400 · trade 585 · admin 50 · tribute 712 · upkeep 408 · charges 656
- DISPATCH: Davout's fortifications strengthen: +12% defense (MAX)
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier checks the order of battle. 'No marshal of infantry can reach Paris, Sire — none of ours stands within reach.' Massena commands our foot at Milan — march him wi…
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 actions unused) Turn 25 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1, unfortify×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 60381 · net +3864 · threat 32 · provinces 28 (+0) · ceiling 382333 · army 54611 · vassals Holland 88 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3400 · trade 585 · admin 50 · tribute 937 · upkeep 408 · charges 700
- DISPATCH: Davout's fortifications decay: 12% → 11%
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 3
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, balance_of_europe_shifted)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)
  - LOG balance_of_europe_shifted: British-led alignment leads the current largest alignment at 38% of active European bloc power.
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 25 — Late September 1806
  - MAILBOX #16 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #21 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (88 → 98); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Berlin. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 2 actions unused) Turn 26 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 63908 · net +3485 · threat 29 · provinces 28 (+0) · ceiling 354250 · army 53908 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3400 · trade 585 · admin 50 · tribute 600 · upkeep 408 · charges 742
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1, fortify×1
- LEDGER treasury 67401 · net +3451 · threat 26 · provinces 28 (+0) · ceiling 354916 · army 53228 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3400 · trade 585 · admin 50 · tribute 600 · upkeep 400 · charges 784
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 20).
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Berlin. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franche-Comte. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only…
- CMD `Soult, unfortify` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Franche-Comte (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 84%
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 2 actions unused) Turn 28 begins!
- SPENT 200g on this turn's orders
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, unfortify×1
- LEDGER treasury 70605 · net +3388 · threat 23 · provinces 28 (+0) · ceiling 352916 · army 55508 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3400 · trade 585 · admin 50 · tribute 600 · upkeep 424 · charges 823
- DISPATCH: Davout is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×2
- LEDGER treasury 74001 · net +3355 · threat 20 · provinces 28 (+0) · ceiling 353583 · army 54808 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3400 · trade 585 · admin 50 · tribute 600 · upkeep 416 · charges 864
- DISPATCH: DRILL COMPLETE: Davout's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 30).
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Berlin. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Soult, drill` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Berlin. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 1 action unused) Turn 30 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- LEDGER treasury 77356 · net +3315 · threat 17 · provinces 28 (+0) · ceiling 353583 · army 54129 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3400 · trade 585 · admin 50 · tribute 600 · upkeep 416 · charges 904
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Berlin, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1, unfortify×1
- LEDGER treasury 80679 · net +3283 · threat 14 · provinces 28 (+0) · ceiling 354250 · army 53471 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3400 · trade 585 · admin 50 · tribute 600 · upkeep 408 · charges 944
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 30).
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Berlin. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mov…
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 2 actions unused) Turn 32 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1, wait×1
- LEDGER treasury 83970 · net +3252 · threat 11 · provinces 28 (+0) · ceiling 354916 · army 52830 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3400 · trade 585 · admin 50 · tribute 600 · upkeep 400 · charges 983
- DISPATCH: Ney's fortifications strengthen: +7% defense (max 8%)
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Berlin. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 actions unused) Turn 33 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, recruit×1
- LEDGER treasury 87230 · net +3558 · threat 8 · provinces 28 (+0) · ceiling 383666 · army 52175 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3400 · trade 585 · admin 50 · tribute 937 · upkeep 392 · charges 1022
- DISPATCH: DRILL COMPLETE: Lannes's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 94).
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Berlin. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franche-Comte. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only…
- CMD `Soult, unfortify` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Rhineland (field levy — no depot; capped at 3,000) (recruitment is drafted in fix…
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 2 actions unused) Turn 34 begins!
- SPENT 345g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1
- LEDGER treasury 90398 · net +3496 · threat 5 · provinces 28 (+0) · ceiling 381666 · army 54541 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3400 · trade 585 · admin 50 · tribute 937 · upkeep 416 · charges 1060
- DISPATCH: Davout is now locked in intensive drill. Cannot receive orders until training completes.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Berlin. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 actions unused) Turn 35 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1, wait×1
- LEDGER treasury 93844 · net +3404 · threat 2 · provinces 28 (+0) · ceiling 377500 · army 53925 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3400 · trade 535 · admin 50 · tribute 937 · upkeep 416 · charges 1102
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Berlin. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franche-Comte. Army is now mobile.
- CMD `Soult, drill` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 2 actions unused) Turn 36 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- LEDGER treasury 97264 · net +3379 · threat 0 · provinces 28 (+0) · ceiling 378833 · army 53327 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3400 · trade 535 · admin 50 · tribute 937 · upkeep 400 · charges 1143
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 40).
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_ai_proposal_refused: 7 approaches from Austria and Prussia are rebuffed (defensive alliance)

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Berlin. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mov…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier checks the order of battle. 'No marshal of infantry can reach Paris, Sire — none of ours stands within reach.' Massena commands our foot at Milan — march him wi…
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 2 actions unused) Turn 37 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1
- LEDGER treasury 100651 · net +3347 · threat 0 · provinces 28 (+0) · ceiling 379500 · army 52746 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3400 · trade 535 · admin 50 · tribute 937 · upkeep 392 · charges 1183
- DISPATCH: Ney's fortifications have crumbled completely!
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 3 actions unused) Turn 38 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 103998 · net +3307 · threat 0 · provinces 28 (+0) · ceiling 379500 · army 52181 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3400 · trade 535 · admin 50 · tribute 937 · upkeep 392 · charges 1223
- DISPATCH: Ney's fortifications strengthen: +2% defense (max 8%)
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Berlin. Army is now mobile.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 3 actions unused) Turn 39 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1
- LEDGER treasury 107305 · net +3267 · threat 0 · provinces 28 (+0) · ceiling 379500 · army 51632 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3400 · trade 535 · admin 50 · tribute 937 · upkeep 392 · charges 1263
- DISPATCH: DRILL COMPLETE: Lannes's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +6 (now 100).
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Berlin. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✗ Marshal Soult is lost to us, Sire — his corps was destroyed at Swabia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission at…
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Franche-Comte (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 85%
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 3 actions unused) Turn 40 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: unfortify×1
- LEDGER treasury 110333 · net +3215 · threat 0 · provinces 28 (+0) · ceiling 378166 · army 54038 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3400 · trade 535 · admin 50 · tribute 937 · upkeep 408 · charges 1299
- DISPATCH: Davout is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Berlin. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Milan (+2% defense).
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 actions unused) Turn 41 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 113556 · net +3184 · threat 0 · provinces 28 (+0) · ceiling 378833 · army 53460 · vassals Holland 98 · Kingdom of Italy 100 · Switzerland 88
  - NET income 3400 · trade 535 · admin 50 · tribute 937 · upkeep 400 · charges 1338
- DISPATCH: Ney is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)

---
finished: **completed** · commands 200 · popups 42 · battles 21
