# Playtest digest — drillfix-cmd-on-austerlitz

seed `austerlitz` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `austerlitz` · dice `austerlitz`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `3d1157842721` (dirty) · content `4346446e7d78` · driver `aef52ad7cbfd`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 78,676 with the corps likely to arrive, up to 96,789 if all march) vs Mack (large force) at Swabia — the balance of force looks favora…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1984, own corps) vs Mack (lost 14668) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Soult, Murat and Bernadotte never arr…
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 7 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a devastating assault! ArchdukeCharles gains the advantage over Bernadotte. Casualties: Archdu… · ArchdukeJohn holds them at Franconia while allies attack from Tyrol! (+1 coordination)
  - ⚔ Archduke Charles (lost 1863, own corps) vs Bernadotte (lost 3909, own corps) — Ney marched to Bernadotte's guns as ordered. It was not enough.
  - ⚔ Archduke John (lost 332, own corps) vs Bernadotte (lost 6756) — The toll on Bernadotte's forces is heavy, Sire. This defeat will be felt.
  - verbs: stance_change×2, attack×2, move×1, retreat×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 2268 · net +2577 · threat 75 · provinces 28 · ceiling 51446 · army 164061 · vassals Holland 97 · Kingdom of Italy 99 · Switzerland 95
  - NET income 3400 · trade 400 · admin 50 · tribute 937 · upkeep 1856 · charges 14 · blockade 250 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +6 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia and Bavaria are rebuffed (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (15,972; expect about 89,585 with the corps likely to arrive, up to 100,449 if all march) vs Mack (substantial force) at Munich — the balance of force looks…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 735, own corps) vs Mack (lost 14280, own corps) — Davout, Massena and Napoleon arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire.
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (21,738; expect about 25,098 with the corps likely to arrive, up to 28,878 if all march) vs Mack (strength unknown) at Tyrol — the balance of force looks…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 313, own corps) vs Mack (lost 14838) — Reinforcements! Ney marched onto the field beside Davout. The enemy's advantage melted away.
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✗ Murat is already in Franche-Comte.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 2 actions unused) Turn 3 begins!
- enemy phase: 6 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Franconia where he stands! (1,460 lost to march) Captured: Bavaria → Austria · ArchdukeCharles delivers an effective strike. ArchdukeCharles gains the advantage over Bernadotte. Casualties: Archduke… · ArchdukeCharles holds them at Swabia while allies attack from Franconia! (+1 coordination)
  - 🏴 Austria: ArchdukeCharles takes Franconia where he stands! (1,460 lost to march) Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 1191) vs Bernadotte (lost 2172, own corps) — Lannes arrived to reinforce Bernadotte, but Soult failed to reach the field in time.
  - ⚔ Archduke Charles (lost 1564) vs Deroy (lost 6332) — Deroy's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×3, retreat×1, stance_change×1, wait×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 4869 · net +2991 · threat 89 · provinces 28 (+0) · ceiling 50460 · army 146655 · vassals Holland 97 · Kingdom of Italy 99 · Switzerland 93
  - NET income 3400 · trade 450 · admin 50 · tribute 937 · upkeep 1324 · charges 188 · requisitions 37 · blockade 281 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Swabia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 8
- DIPLO +7 medium/low (diplomatic_treaty_signed ×3, diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 26 approaches from Bavaria, Austria and Prussia are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✗ Cannot attack elsewhere while engaged with enemy forces! Archduke John must be dealt with first.
- CMD `Davout, attack Mack` → ✗ Cannot attack elsewhere while engaged with enemy forces! Archduke John must be dealt with first.
- CMD `Lannes, move to Swabia` → ✗ Cannot move into Swabia - enemy forces present! Use ATTACK to engage Archduke Charles.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 676 gold (×3 at war) (×1.13 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 4 actions unused) Turn 4 begins!
- SPENT 676g on this turn's orders
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Swabia where he stands! (1,089 lost to march) Captured: Bavaria → Austria · ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Murat. Casualties: ArchdukeCh…
  - 🏴 Austria: ArchdukeCharles takes Swabia where he stands! (1,089 lost to march) Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 2102) vs Murat (lost 5491) — Where was Soult? Murat held the field alone — reinforcement never came.
  - verbs: attack×2, move×1, wait×1
  - ⚡ AUTONOMOUS: [Combat] Murat leads the charge! (Aggressive: +15% attack)
  - ⚔ Murat (lost 2179, own corps) vs Archduke Charles (lost 6710) — Reinforcements from Massena and Napoleon bolstered Murat's position — though Soult never arrived, Sire.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 6820 · net +2846 · threat 87 · provinces 28 (+0) · ceiling 33361 · army 135196 · vassals Holland 95 · Kingdom of Italy 97 · Switzerland 89
  - NET income 3382 · trade 525 · admin 50 · tribute 937 · upkeep 1068 · charges 516 · contributions 82 · requisitions 37 · blockade 329 · admiralty 90
- DISPATCH: Sire — Murat was mauled at Franche-Comte: a quarter of his corps — 5,491 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 8
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 19 approaches rebuffed, chiefly from Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✗ No intelligence on Mack's position, Sire. Scout for him before Ney can give chase.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Tyrol. Defense bonus: +7% (grows +3% per turn, max…
- CMD `Massena, move to Tyrol` → ✓ Massena moves from Munich to Tyrol. Tyrol falls to France! (was Austria) (2,075 lost to march)
  - POPUP capture_choice[capture]: Tyrol, Massena → secure
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 1 action unused) Turn 5 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces strike with perfect coordination! ArchdukeCharles gains the advantage over Murat. Casualties: …
  - 🏴 Austria: Casualties: ArchdukeCharles 1,340, Murat's army 7,218. Both armies remain in the field. Franche-Comte has been captured by Austria!
  - ⚔ Archduke Charles (lost 1340) vs Murat (lost 4800, own corps) — Napoleon's timely arrival aided Murat. Soult, however, was conspicuously absent.
  - verbs: attack×1, wait×1
- LEDGER treasury 9502 · net +2593 · threat 87 · provinces 28 (+0) · ceiling 31624 · army 119620 · vassals Holland 93 · Kingdom of Italy 95 · Switzerland 85
  - NET income 3336 · trade 587 · admin 50 · tribute 937 · upkeep 928 · charges 879 · occupation 52 · blockade 368 · admiralty 90
- DISPATCH: Sire — Franche-Comte has fallen. Enemy colours fly over French homeland soil. A garrison you detach (3,000 men) holds a province against a march, as does any garrison of 5,000; a corps standing there…
  - TURN EVENTS 8
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG ai_ai_proposal_refused: 3 approaches from Austria and Bavaria are rebuffed (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven

## Turn 5 — Late November 1805
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (13,314; expect about 43,259 with the corps likely to arrive, up to 43,525 if all march) vs Archduke Charles (substantial force) at Munich — the balance of …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1489, own corps) vs Archduke Charles (lost 2633) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
- CMD `Lannes, attack Mack` → ✗ No intelligence on Mack's position, Sire. Scout for him before Lannes can give chase.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia. Swabia falls to France! (was Austria) (914 lost to march)
  - POPUP capture_choice[capture]: Swabia, Soult → secure
- CMD `Murat, move to Swabia` → ✓ Murat moves from Lorraine to Swabia (91 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 1 action unused) Turn 6 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · Deroy takes Franconia where he stands! (70 lost to march — forward supply lines reduce losses) Captured: Austria → Bava…
  - 🏴 Austria: [!] Ney's troops are BROKEN (morale 0%)! FORCED RETREAT! ArchdukeCharles advances into Milan. (543 lost to march) Milan has been captured by Austria!
  - 🏴 Bavaria: Deroy takes Franconia where he stands! (70 lost to march — forward supply lines reduce losses) Captured: Austria → Bavaria
  - ⚔ Archduke Charles (lost 253) vs Ney (lost 6411) — A grievous defeat for Ney, Sire. The losses are severe.
  - verbs: attack×2, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
  - POPUP diplomatic_dialogue: Austria, armistice_losing #10 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
  - POPUP diplomatic_dialogue: Switzerland, client_petition #11 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (79 → 89); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 2 · Austria armistice losing · Switzerland client petition
- LEDGER treasury 11212 · net +1757 · threat 77 · provinces 29 (+1) · ceiling 24684 · army 105167 · vassals Holland 89 · Switzerland 89
  - NET income 3357 · trade 599 · admin 50 · tribute 337 · upkeep 816 · charges 1201 · occupation 104 · blockade 375 · admiralty 90
- DISPATCH: Sire — Ney, crowned four turns ago, has been beaten in the field.
  - RAIL nation_eliminated: KingdomOfItaly has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 9
- DIPLO +2 medium/low (diplomatic_dp_regen, agenda_shift)

## Turn 6 — Early December 1805
- CMD `Ney, drill` → ✗ Ney is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier advises caution. 'Swabia is in Unrest (stability 35/100). The populace will not answer our call until stability exceeds 50.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 2 actions unused) Turn 7 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 13054 · net +1596 · threat 75 · provinces 29 (+0) · ceiling 24994 · army 103326 · vassals Holland 89 · Switzerland 88
  - NET income 3433 · trade 599 · admin 50 · tribute 337 · upkeep 800 · charges 1476 · occupation 82 · blockade 375 · admiralty 90
- DISPATCH: Sire — Ney, Davout and Massena have been 4 turns over what Tyrol can feed. 5,633 men. The country will ask where the army went. A supply depot at Tyrol would ease it; Franconia can feed 60,000 more a…
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 5
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +4 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Bavaria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 9 approaches from Austria and Sardinia are rebuffed (defensive alliance)
  - LOG nation_eliminated: KingdomOfItaly has been eliminated from the war.

## Turn 7 — Late December 1805
- CMD `Ney, attack Archduke Charles` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Davout, move to Bohemia` → ✓ Davout moves from Tyrol to Bohemia (177 lost to march)
- CMD `Murat, attack Archduke Charles` → ✗ Cannot attack ArchdukeCharles — armistice with Austria (4 turns remaining).
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 3 actions unused) Turn 8 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles assaults the Munich garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 3,472 troops. G…
  - verbs: move×1, attack×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 15022 · net +1758 · threat 73 · provinces 29 (+0) · ceiling 31475 · army 102505 · vassals Holland 89 · Switzerland 87
  - NET income 3479 · trade 599 · admin 50 · tribute 337 · upkeep 792 · charges 1390 · occupation 60 · blockade 375 · admiralty 90
- DISPATCH: Sire — Leon has been taken by Britain.
  - TURN EVENTS 6
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 2 more — Bavaria is not forgiven
  - LOG ai_ai_proposal_refused: Denmark rebuffs Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: 8 approaches rebuffed, chiefly from Austria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: Russia rebuffs Spain (open borders agreement)

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✗ Cannot attack ArchdukeCharles — armistice with Austria (3 turns remaining).
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Tyr…
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shift…
- CMD `Massena, move to Milan` → ✗ Cannot enter Milan — the evacuation corridor with Austria grants safe passage HOME to stranded corps, not entry. Massena can already reach the body of the realm from whe…
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 1 action unused) Turn 9 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles assaults the Munich garrison! Garrison collapses (7,000 -> 0). ArchdukeCharles loses 2,430 troops in th… · ArchdukeCharles marches from Munich into Franconia unopposed! (146 lost to march) Captured: Bavaria → Austria · ArchdukeJohn marches from Hungary into Carniola unopposed! (128 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -121g, Bavaria -175g. Captured: Bavaria → Austria
  - 🏴 Austria: ArchdukeCharles marches from Munich into Franconia unopposed! (146 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: ArchdukeJohn marches from Hungary into Carniola unopposed! (128 lost to march) Captured: Bavaria → Austria
  - verbs: attack×3, move×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
  -     ↳ Massena's grievance runs its course.
- LEDGER treasury 16756 · net +1543 · threat 71 · provinces 29 (+0) · ceiling 30781 · army 101877 · vassals Holland 89 · Switzerland 86
  - NET income 3481 · trade 599 · admin 50 · tribute 337 · upkeep 776 · charges 1623 · occupation 60 · blockade 375 · admiralty 90
- DISPATCH: Sire — Munich has been taken by Austria.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 7
- COURTS: The court of Austria eases over Revanche — an ultimatum is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — service to the strong is now the length of its tether.
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Tyrol. Army is now mobile.
- CMD `Lannes, move to Bohemia` → ✗ Lannes is fortified at Lorraine and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 11.
- CMD `recruit 10000 cavalry with Murat` → ✓ Murat recruits 3,000 cavalry at Swabia (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed corps of 5,000, Sire — your 10,000 is noted) - Cost: 155…
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 2 actions unused) Turn 10 begins!
- SPENT 1552g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Russia, Prussia, Spain and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×2
- ORDER Massena [continues]: Massena marches to Franconia. 1 region to Swabia.
- ORDER Ney [continues]: Ney marches to Franconia. 1 region to Swabia.
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte demands to be heard → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 16883 · net +1514 · threat 69 · provinces 29 (+0) · ceiling 30250 · army 103987 · vassals Holland 89 · Switzerland 85
  - NET income 3522 · trade 599 · admin 50 · tribute 337 · upkeep 800 · charges 1684 · occupation 45 · blockade 375 · admiralty 90
- DISPATCH: Sire — Davout, Massena and Ney are no nearer home, and the safe passage runs out in 0 turns. After that their corps will be interned where they stand.
  - TURN EVENTS 7
- DIPLO +4 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG british_subsidy: Britain's gold: 200g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG ai_ai_proposal_refused: 17 approaches rebuffed, chiefly from Prussia and Austria (open borders agreement)

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✗ Ney is already in Franconia.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Bohemia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortif…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Croatia.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 3 actions unused) Turn 11 begins!
- enemy phase: 7 actions, 3 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight. — Castanos's forces press forward aggressively. Castanos gains the advantage over Paget. Casualties: Castanos 500, Paget … · Castanos holds them at Leon while allies attack from Aragon! (+1 coordination) · Deroy marches from Tyrol into Munich unopposed! (197 lost to march) Captured: Austria → Bavaria
  - 🏴 Spain: [!] Paget's troops are BROKEN (morale 0%)! FORCED RETREAT! Leon has been captured by Spain!
  - 🏴 Bavaria: Deroy moves from Croatia to Carniola. Carniola falls to Bavaria!
  - 🏴 Bavaria: Deroy marches from Tyrol into Munich unopposed! (197 lost to march) Captured: Austria → Bavaria
  - ⚔ Castanos (lost 500) vs Paget (lost 1716) — Paget's aggressive posture left the troops exposed when Castanos's attack came.
  - ⚔ Castanos (lost 203) vs Paget (lost 1110) — Paget was caught in an aggressive posture when Castanos struck, Sire. A defensive stance would have served better. And …
  - verbs: move×3, attack×3, break_square×1
- ORDER Massena [completed]: Massena arrives at Swabia. Massena: "Done — and I trust the next order has more fire in it."
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 18523 · net +1449 · threat 67 · provinces 29 (+0) · ceiling 30969 · army 101765 · vassals Holland 89 · Switzerland 84
  - NET income 3549 · trade 599 · admin 50 · tribute 337 · upkeep 768 · charges 1923 · requisitions 100 · occupation 30 · blockade 375 · admiralty 90
- DISPATCH: Sire — Davout and Ney are no nearer home, and the safe passage runs out in 0 turns. After that their corps will be interned where they stand.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL diplomatic_armistice_expired_war: The armistice between Austria and France has collapsed. War resumes!
  - TURN EVENTS 5
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- COURTS: The court of Austria hardens over Revanche — prepared now to go as far as war.
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: 10 approaches from Austria and Sardinia are rebuffed (defensive alliance)
  - LOG ai_ai_proposal_refused: 28 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)

## Turn 11 — Late February 1806
  - MAILBOX #10 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #12 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #13 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain + Russia (6 pairs resolved). Status quo: Swabia and Tyrol stay ours by the treaty — titled. Status quo: Franche-Comte stays Austrian by the treaty. Status quo: Carniola and Croatia stay Bavarian by the treaty. Status quo: Franconia stays Austrian by the treaty. → display-only
- CMD `Ney, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Lannes, attack Archduke John` → ✗ Lannes is fortified at Lorraine and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✗ Cannot enter Franconia — the evacuation corridor with Austria grants safe passage HOME to stranded corps, not entry. Murat can already reach the body of the realm from w…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 2 actions unused) Turn 12 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 22101 · net +3535 · threat 33 · provinces 29 (+0) · ceiling 316666 · army 100105 · vassals Holland 87 · Switzerland 83
  - NET income 3552 · trade 635 · admin 50 · tribute 337 · upkeep 768 · charges 241 · occupation 30
- DISPATCH: Sire — Soult, Murat and Massena stand 63,356 men at Swabia, which feeds 60,000. 3,356 too many. 2,792 men lost in 2 turns. A supply depot at Swabia would ease it; Rhineland can feed 60,000 more and L…
  - RAIL settlement_summary: Settlement of France + Spain + Holland + Bavaria vs Britain + Austria + Russia: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 5
- COURTS: The court of Britain eases over The Low Countries — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: And 2 other courts stir at their own designs.
- DIPLO +7 medium/low (diplomatic_coalition_dissolved, status_quo_titled, law_enacted_abroad, diplomatic_dp_regen, blockade_broken ×3)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 67 to 33.
  - LOG ai_ai_proposal_refused: 9 courts rebuff Bavaria (open borders agreement)

## Turn 12 — Early March 1806
  - MAILBOX #11 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #14 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (87 → 97); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 15% -> 21%
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 25072 · net +3158 · threat 33 · provinces 29 (+0) · ceiling 288166 · army 101440 · vassals Holland 96 · Switzerland 82
  - NET income 3555 · trade 635 · admin 50 · upkeep 776 · charges 276 · occupation 30
- DISPATCH: Sire — Davout and Ney are no nearer home, and the safe passage runs out in 2 turns. After that their corps will be interned where they stand.
  - TURN EVENTS 6
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Prussia and Bavaria rebuff Sardinia (defensive alliance)
  - LOG ai_ai_proposal_refused: 6 courts rebuff Bavaria (open borders agreement)

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Davout, move to Franconia` → ✓ Davout moves from Bohemia to Franconia (175 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 actions unused) Turn 14 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 28241 · net +3356 · threat 33 · provinces 29 (+0) · ceiling 307833 · army 99656 · vassals Holland 95 · Switzerland 81
  - NET income 3558 · trade 635 · admin 50 · tribute 225 · upkeep 768 · charges 314 · occupation 30
- DISPATCH: Sire — Davout and Ney are no nearer home, and the safe passage runs out in 1 turn. After that their corps will be interned where they stand.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 14 — Early April 1806
- CMD `Lannes, fortify` → ✗ Lannes is already fortified at Lorraine (+2% defense).
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 3 actions unused) Turn 15 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 31624 · net +3342 · threat 33 · provinces 29 (+0) · ceiling 310083 · army 98099 · vassals Holland 94 · Switzerland 80
  - NET income 3561 · trade 635 · admin 50 · tribute 225 · upkeep 744 · charges 355 · occupation 30
- DISPATCH: Sire — Davout and Ney are no nearer home, and the safe passage runs out in 0 turns. After that their corps will be interned where they stand.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)

## Turn 15 — Late April 1806
  - MAILBOX #12 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #15 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (80 → 90); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 93%
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- SPENT 200g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 34505 · net +3237 · threat 33 · provinces 29 (+0) · ceiling 304250 · army 77258 · vassals Holland 93 · Switzerland 90
  - NET income 3564 · trade 635 · admin 50 · upkeep 592 · charges 390 · occupation 30
- DISPATCH: Sire — Marshal Ney's corps was interned at Franconia by Austria — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG ai_ai_proposal_refused: Prussia and Bavaria rebuff Sardinia (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples and Denmark rebuff Bavaria (open borders agreement)

## Turn 16 — Early May 1806
- CMD `Ney, move to Bohemia` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Lorraine. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action unused) Turn 17 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 37753 · net +3209 · threat 33 · provinces 29 (+0) · ceiling 305166 · army 75697 · vassals Holland 92 · Switzerland 90
  - NET income 3567 · trade 635 · admin 50 · upkeep 584 · charges 429 · occupation 30
- DISPATCH: Sire — Marshal Davout's corps was interned at Franconia by Austria — its safe passage had expired and it had not come home. The men are disarmed and the colours are lost.
  - TURN EVENTS 3
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Sardinia eases over The House of Savoy Restored — gold is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Bavaria lapses

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Davout, fortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Swabia (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 3 actions unused) Turn 18 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 40981 · net +3190 · threat 33 · provinces 29 (+0) · ceiling 306750 · army 74186 · vassals Holland 91 · Switzerland 90
  - NET income 3570 · trade 635 · admin 50 · upkeep 568 · charges 467 · occupation 30
- DISPATCH: Lannes is now locked in intensive drill. Cannot receive orders until training completes.
  - TURN EVENTS 4
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sardinia (defensive alliance)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Sardinia (defensive alliance)

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier checks the order of battle. 'No marshal of infantry can reach Paris, Sire — none of ours stands within reach.' Lannes commands our foot at Lorraine — march him …
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 44182 · net +3162 · threat 33 · provinces 29 (+0) · ceiling 307666 · army 72706 · vassals Holland 90 · Switzerland 90
  - NET income 3573 · trade 635 · admin 50 · upkeep 560 · charges 506 · occupation 30
- DISPATCH: DRILL COMPLETE: Lannes's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 31).
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Davout, unfortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 47371 · net +3488 · threat 33 · provinces 29 (+0) · ceiling 338000 · army 71256 · vassals Holland 89 · Switzerland 90
  - NET income 3576 · trade 635 · admin 50 · tribute 337 · upkeep 536 · charges 544 · occupation 30
- DISPATCH: Soult's fortifications decay: 12% → 11%
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Denmark rebuffs Bavaria (open borders agreement)

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 50862 · net +3449 · threat 31 · provinces 29 (+0) · ceiling 338250 · army 69835 · vassals Holland 88 · Switzerland 90
  - NET income 3579 · trade 635 · admin 50 · tribute 337 · upkeep 536 · charges 586 · occupation 30
- DISPATCH: Soult's fortifications decay: 11% → 10%
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 3
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)

## Turn 21 — Late July 1806
  - MAILBOX #13 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #16 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (88 → 98); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, fortify` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Davout, drill` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Swabia (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed …
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 3 actions unused) Turn 22 begins!
- SPENT 345g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 53595 · net +3066 · threat 29 · provinces 29 (+0) · ceiling 309083 · army 71381 · vassals Holland 98 · Switzerland 90
  - NET income 3582 · trade 635 · admin 50 · upkeep 552 · charges 619 · occupation 30
- DISPATCH: Soult's fortifications decay: 10% → 9%
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- COURTS: The court of Sweden eases over Scourge of the Usurper — service to the strong is now the length of its tether.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Swabia. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 actions unused) Turn 23 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 56672 · net +3265 · threat 27 · provinces 29 (+0) · ceiling 328750 · army 69957 · vassals Holland 98 · Switzerland 90
  - NET income 3585 · trade 635 · admin 50 · tribute 225 · upkeep 544 · charges 656 · occupation 30
- DISPATCH: Lannes's fortifications strengthen: +2% defense (max 8%)
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Davout, fortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Lorraine. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 2 actions unused) Turn 24 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 59964 · net +3253 · threat 25 · provinces 29 (+0) · ceiling 331000 · army 68560 · vassals Holland 98 · Switzerland 90
  - NET income 3588 · trade 635 · admin 50 · tribute 225 · upkeep 520 · charges 695 · occupation 30
- DISPATCH: DRILL COMPLETE: Soult's corps sharpens in a single day — Drillmaster of Boulogne. +20% attack bonus ready for next battle. The ranks steady with the work: morale +7 (now 100).
  - TURN EVENTS 2
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 93%
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 actions unused) Turn 25 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 62973 · net +3196 · threat 23 · provinces 29 (+0) · ceiling 329250 · army 70132 · vassals Holland 98 · Switzerland 90
  - NET income 3591 · trade 635 · admin 50 · tribute 225 · upkeep 544 · charges 731 · occupation 30
- DISPATCH: Massena's fortifications have crumbled completely!
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Davout, unfortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 2 actions unused) Turn 26 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 66188 · net +3176 · threat 21 · provinces 29 (+0) · ceiling 330833 · army 68732 · vassals Holland 98 · Switzerland 90
  - NET income 3594 · trade 635 · admin 50 · tribute 225 · upkeep 528 · charges 770 · occupation 30
- DISPATCH: Soult's fortifications strengthen: +7% defense (max 12%)
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 69367 · net +3141 · threat 19 · provinces 29 (+0) · ceiling 331083 · army 67361 · vassals Holland 98 · Switzerland 90
  - NET income 3597 · trade 635 · admin 50 · tribute 225 · upkeep 528 · charges 808 · occupation 30
- DISPATCH: Soult's fortifications decay: 7% → 6%
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 41% -> 40%
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 2 actions unused) Turn 28 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 72288 · net +3109 · threat 17 · provinces 29 (+0) · ceiling 331333 · army 68957 · vassals Holland 98 · Switzerland 90
  - NET income 3600 · trade 635 · admin 50 · tribute 225 · upkeep 528 · charges 843 · occupation 30
- DISPATCH: Lannes's fortifications have crumbled completely!
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Swabia. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 75405 · net +3417 · threat 15 · provinces 29 (+0) · ceiling 360083 · army 67582 · vassals Holland 98 · Switzerland 90
  - NET income 3600 · trade 635 · admin 50 · tribute 562 · upkeep 520 · charges 880 · occupation 30
- DISPATCH: Lannes's fortifications strengthen: +2% defense (max 8%)
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Lorraine. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 2 actions unused) Turn 30 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 78838 · net +3391 · threat 13 · provinces 29 (+0) · ceiling 361416 · army 66234 · vassals Holland 98 · Switzerland 90
  - NET income 3600 · trade 635 · admin 50 · tribute 562 · upkeep 504 · charges 922 · occupation 30
- DISPATCH: DRILL COMPLETE: Soult's corps sharpens in a single day — Drillmaster of Boulogne. +20% attack bonus ready for next battle. The ranks steady with the work: morale +7 (now 100).
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 2
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier checks the order of battle. 'No marshal of infantry can reach Paris, Sire — none of ours stands within reach.' Lannes commands our foot at Lorraine — march him …
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 82237 · net +3359 · threat 11 · provinces 29 (+0) · ceiling 362083 · army 64912 · vassals Holland 98 · Switzerland 90
  - NET income 3600 · trade 635 · admin 50 · tribute 562 · upkeep 496 · charges 962 · occupation 30
- DISPATCH: Massena's fortifications have crumbled completely!
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Davout, unfortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 2 actions unused) Turn 32 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 85604 · net +3326 · threat 9 · provinces 29 (+0) · ceiling 362750 · army 63616 · vassals Holland 98 · Switzerland 90
  - NET income 3600 · trade 635 · admin 50 · tribute 562 · upkeep 488 · charges 1003 · occupation 30
- DISPATCH: Soult's fortifications strengthen: +7% defense (max 12%)
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 88938 · net +3294 · threat 7 · provinces 29 (+0) · ceiling 363416 · army 62347 · vassals Holland 98 · Switzerland 90
  - NET income 3600 · trade 635 · admin 50 · tribute 562 · upkeep 480 · charges 1043 · occupation 30
- DISPATCH: Soult's fortifications decay: 7% → 6%
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Swabia (field levy — no depot; capped at 3,000) (recruitment is drafted in fixed …
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 2 actions unused) Turn 34 begins!
- SPENT 345g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 91866 · net +3259 · threat 5 · provinces 29 (+0) · ceiling 363416 · army 64044 · vassals Holland 98 · Switzerland 90
  - NET income 3600 · trade 635 · admin 50 · tribute 562 · upkeep 480 · charges 1078 · occupation 30
- DISPATCH: Lannes's fortifications have crumbled completely!
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 3
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Swabia. Army is now mobile.
- CMD `Ney, drill` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 3 actions unused) Turn 35 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 95095 · net +3190 · threat 3 · provinces 29 (+0) · ceiling 360916 · army 62766 · vassals Holland 98 · Switzerland 90
  - NET income 3600 · trade 597 · admin 50 · tribute 562 · upkeep 472 · charges 1117 · occupation 30
- DISPATCH: Lannes's fortifications strengthen: +2% defense (max 8%)
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Lorraine. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 2 actions unused) Turn 36 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 98293 · net +3160 · threat 1 · provinces 29 (+0) · ceiling 361583 · army 61513 · vassals Holland 98 · Switzerland 90
  - NET income 3600 · trade 597 · admin 50 · tribute 562 · upkeep 464 · charges 1155 · occupation 30
- DISPATCH: DRILL COMPLETE: Soult's corps sharpens in a single day — Drillmaster of Boulogne. +20% attack bonus ready for next battle.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Ca…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Swabia (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 100% -> 92%
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 3 actions unused) Turn 37 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 101214 · net +3109 · threat 0 · provinces 29 (+0) · ceiling 360250 · army 63226 · vassals Holland 98 · Switzerland 90
  - NET income 3600 · trade 597 · admin 50 · tribute 562 · upkeep 480 · charges 1190 · occupation 30
- DISPATCH: Massena's fortifications have crumbled completely!
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 2 actions unused) Turn 38 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 104339 · net +3087 · threat 0 · provinces 29 (+0) · ceiling 361583 · army 61964 · vassals Holland 98 · Switzerland 90
  - NET income 3600 · trade 597 · admin 50 · tribute 562 · upkeep 464 · charges 1228 · occupation 30
- DISPATCH: Soult's fortifications strengthen: +7% defense (max 12%)
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 107426 · net +3050 · threat 0 · provinces 29 (+0) · ceiling 361583 · army 60728 · vassals Holland 98 · Switzerland 90
  - NET income 3600 · trade 597 · admin 50 · tribute 562 · upkeep 464 · charges 1265 · occupation 30
- DISPATCH: Soult's fortifications decay: 7% → 6%
  - TURN EVENTS 4
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 60% -> 55%
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 3 actions unused) Turn 40 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 110246 · net +3009 · threat 0 · provinces 29 (+0) · ceiling 360916 · army 62456 · vassals Holland 98 · Switzerland 90
  - NET income 3600 · trade 597 · admin 50 · tribute 562 · upkeep 472 · charges 1298 · occupation 30
- DISPATCH: Massena's fortifications strengthen: +2% defense (max 8%)
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✗ Marshal Ney is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commission a…
- CMD `Massena, fortify` → ✗ Massena is already fortified at Swabia (+2% defense).
- CMD `Davout, fortify` → ✗ Marshal Davout is lost to us, Sire — his corps was destroyed at Franconia. His name cannot lead the army again. The Marshalate holds men yet — Oudinot awaits a commissio…
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 actions unused) Turn 41 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Sweden defensive alliance
- LEDGER treasury 113263 · net +2980 · threat 0 · provinces 29 (+0) · ceiling 361583 · army 61208 · vassals Holland 98 · Switzerland 90
  - NET income 3600 · trade 597 · admin 50 · tribute 562 · upkeep 464 · charges 1335 · occupation 30
- DISPATCH: Massena's fortifications have crumbled completely!
  - RAIL diplomatic_ai_proposal: An envoy from Sweden has arrived with a proposal.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)

---
finished: **completed** · commands 200 · popups 33 · battles 14
