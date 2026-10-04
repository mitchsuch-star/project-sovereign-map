# Playtest digest — CMD-H

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `d10182082767` (dirty) · content `1ecab161811e` · driver `fe441ad83bb4`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 85,373 with the corps likely to arrive, up to 96,789 if all march) vs Mack (large force) at Swabia — the balance of force looks favora…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 2157, own corps) vs Mack (lost 17054) — Reinforcements from Davout, Lannes, Murat and Napoleon bolstered Ney's position — though Soult and Bernadotte never arr… — The corps system brought Murat in. — Berthier: the corps marched apart and arrived together.
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Brutal stalemate between Archduke Charles and Massena. Heavy casu…
  - ⚔ Archduke Charles (lost 4213) vs Massena (lost 6225) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - verbs: attack×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1645 · net +1469 · threat 76 · provinces 28 · ceiling 34790 · army 173942 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 99
  - NET income 2590 · trade 400 · admin 50 · tribute 895 · upkeep 2126 · blockade 250 · admiralty 90
- DISPATCH: Supply cost you 2,636 men, at Swabia.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +8 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (20,808; expect about 94,391 with the corps likely to arrive, up to 104,979 if all march) vs Mack (substantial force) at Munich — the balance of force looks…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 803, own corps) vs Mack (lost 21656) — Davout, Massena and Teulie arrived to reinforce Ney, but Napoleon failed to reach the field in time. — Berthier: the corps marched apart and arrived together.
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (23,071; expect about 40,115 with the corps likely to arrive) vs Mack (large force) at Tyrol — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 5258, own corps) vs Archduke Charles (lost 2031, own corps) — Ney marched to Davout's guns as ordered. It was not enough.
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✓ Murat moves from Swabia to Franche-Comte
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 1 action unused) Turn 3 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · Deroy's forces advance steadily. Archduke John holds the line. Casualties: Deroy 3,032, Archduke John 1,631. Both armie… · Deroy engages in solid combat. Archduke John holds the line. Casualties: Deroy 2,866, Archduke John 1,282. Both armies …
  - ⚔ Archduke Charles (lost 2018) vs Bernadotte (lost 5561) — Bernadotte's army has been badly mauled. Archduke Charles proved the stronger force today.
  - ⚔ Deroy (lost 3032) vs Archduke John (lost 1631) — Archduke John's fortifications held firm, Sire. Deroy broke against our walls.
  - ⚔ Deroy (lost 2866) vs Archduke John (lost 1282) — The prepared defenses proved their worth. Deroy could not dislodge Archduke John.
  - verbs: attack×3, fortify×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 2971 · net +2005 · threat 82 · provinces 28 (+0) · ceiling 35725 · army 154533 · vassals Holland 97 · Kingdom of Italy 96 · Switzerland 94
  - NET income 2590 · trade 450 · admin 50 · tribute 901 · upkeep 1556 · charges 59 · blockade 281 · admiralty 90
- DISPATCH: Sire — Bernadotte was mauled at Franconia: a quarter of his corps — 5,561 men — lost in a single action.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 8
- DIPLO +8 medium/low (diplomatic_treaty_signed ×3, diplomatic_we_threshold ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 26 approaches from Prussia, Bavaria and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (16,150; expect about 24,894 with the corps likely to arrive, up to 29,891 if all march) vs Mack (11,380 men) at Tyrol — the balance of force looks even — a…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1306, own corps) vs Mack (lost 3465, own corps) — Massena and Teulie's timely arrival aided Ney. Davout, however, was conspicuously absent.
- CMD `Davout, attack Mack` → ✓ Davout: 'Enemy holds Tyrol — destination blocked. How shall I proceed, Sire?'
  - POPUP strategic_interrupt: Davout, contact, Davout: 'Enemy holds Tyrol — destination blocked. How shall I proceed, Sire?' → attack
  - ↳ Davout attacks ArchdukeJohn and wins! Continuing the pursuit. MUSTER — Davout (16,998; expect about 71,839 with the corps likely to arrive) vs Archduke John (12,979 men) at Tyrol — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 320, own corps) vs Archduke John (lost 6681) — Davout broke through fortified positions — extraordinary courage from the men.
  - POPUP capture_choice[capture]: Tyrol, Davout → secure
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Rhineland to Swabia (167 lost to march)
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 686 gold (×3 at war) (×1.14 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 1 action unused) Turn 4 begins!
- SPENT 686g on this turn's orders
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Deroy launches a decisive assault. Deroy gains the advantage over Mack. Casualties: Deroy 169, Mack 4,843. Both armies … · Deroy holds them at Bohemia while allies attack from Franconia! (+1 coordination)
  - 🏴 Bavaria: [!] MARSHAL CAPTURED — Mack is taken by Bavaria at Bohemia!
  - 🏴 Bavaria: [!] Archduke John's troops are BROKEN (morale 0%)! FORCED RETREAT! Bohemia has been captured by Bavaria!
  - ⚔ Deroy (lost 169) vs Mack (lost 4843) — A grievous defeat for Mack, Sire. The losses are severe. And Mack was taken on that field — Bavaria holds him.
  - ⚔ Deroy (lost 192) vs Archduke John (lost 2649) — The toll on Archduke John's forces is heavy, Sire. This defeat will be felt.
  - verbs: attack×2, wait×1, move×1
- ORDER Davout [active]: Davout is pursuing Mack (1 turn remaining).
  - POPUP marshal_audience: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
  -     ↳ Massena's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 4377 · net +1962 · threat 88 · provinces 29 (+1) · ceiling 24812 · army 150737 · vassals Holland 99 · Kingdom of Italy 97 · Switzerland 94
  - NET income 2609 · trade 525 · admin 50 · tribute 905 · upkeep 1428 · charges 228 · occupation 52 · blockade 329 · admiralty 90
- DISPATCH: Sire — Marshal Davout holds the field at Tyrol — Archduke John's corps is driven from Tyrol yet again — broken, and fleeing.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 6
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen, agenda_shift)
  - LOG ai_ai_proposal_refused: 25 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✗ Mack is a prisoner of Bavaria at Munich, Sire — he leads no army.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Tyrol. Defense bonus: +7% (grows +3% per turn, max…
- CMD `Massena, move to Tyrol` → ✗ Massena is already in Tyrol.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 actions unused) Turn 5 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Vienna into Bohemia unopposed! (1,287 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: ArchdukeCharles marches from Vienna into Bohemia unopposed! (1,287 lost to march) Captured: Bavaria → Austria
  - verbs: attack×1, fortify×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 6557 · net +1861 · threat 86 · provinces 29 (+0) · ceiling 25316 · army 147373 · vassals Holland 99 · Kingdom of Italy 97 · Switzerland 92
  - NET income 2610 · trade 587 · admin 50 · tribute 910 · upkeep 1334 · charges 452 · occupation 52 · blockade 368 · admiralty 90
- DISPATCH: Sire — Bohemia has been taken by Austria.
  - TURN EVENTS 8
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: Naples, Denmark and Bavaria rebuff Prussia (open borders agreement)
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — Bavaria is not forgiven
  - LOG ai_ai_proposal_refused: 17 approaches rebuffed, chiefly from Prussia and Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: 2 approaches from Prussia and Spain are rebuffed (open borders agreement)

## Turn 5 — Late November 1805
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (12,835; expect about 19,526 with the corps likely to arrive) vs Archduke Charles (41,636 men) at Bohemia — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 5003, own corps) vs Archduke Charles (lost 1456) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
- CMD `Lannes, attack Mack` → ✗ Mack is a prisoner of Bavaria at Munich, Sire — he leads no army.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (990 lost to march)
- CMD `Murat, move to Swabia` → ✓ Murat moves from Franche-Comte to Swabia (234 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 1 action unused) Turn 6 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ORDER Teulie [retired]: Teulie's question is overtaken, Sire — Teulie has marched clear of Bohemia. He awaits new orders.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  -     ↳ Lannes's grievance runs its course.
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #9 → grant the petition
  - POPUP proposal_result: Tyrol is ceded to the Kingdom of Italy. Loyalty +8 (92 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. Our net rises by 6g a turn — 63g of income forfeited, 30g of occupation relieved, 47g returned as tribute at today's 75% rate, the force limit falls 2,500 (+8g surcharge). → display-only
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 8564 · net +2151 · threat 84 · provinces 28 (-1) · ceiling 36128 · army 135610 · vassals Holland 97 · Kingdom of Italy 100 · Switzerland 88
  - NET income 2590 · trade 587 · admin 50 · tribute 961 · upkeep 1068 · charges 511 · blockade 368 · admiralty 90
- DISPATCH: Sire — Ney, crowned four turns ago, has been beaten in the field.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 8
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)

## Turn 6 — Early December 1805
- CMD `Ney, drill` → ✗ Ney is recovering from retreat and cannot drill. Recovery: 2 turns remaining.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 2 actions unused) Turn 7 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeJohn marches from Bohemia into Carniola unopposed! (162 lost to march) Captured: Bavaria → Austria
  - 🏴 Austria: ArchdukeJohn marches from Bohemia into Carniola unopposed! (162 lost to march) Captured: Bavaria → Austria
  - verbs: move×3, unfortify×1, attack×1
  - POPUP marshal_petition: jealousy_confrontation, Marshal Murat demands to be heard → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #10 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (86 → 96); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 10454 · net +1433 · threat 82 · provinces 28 (+0) · ceiling 23339 · army 131937 · vassals Holland 97 · Kingdom of Italy 100 · Switzerland 96
  - NET income 2590 · trade 587 · admin 50 · tribute 742 · upkeep 1028 · charges 940 · contributions 110 · blockade 368 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Gascony. No French corps stands in his path.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 9
- DIPLO +3 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, coercive_demand)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
- CMD `Ney, attack Archduke Charles` → ✗ Ney is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Davout, move to Bohemia` → ✗ Cannot move into Bohemia - enemy forces present! Use ATTACK to engage Archduke Charles.
- CMD `Murat, attack Archduke Charles` → ✓ MUSTER — Murat (19,067; expect about 21,732 with the corps likely to arrive, up to 29,337 if all march) vs Archduke Charles (40,180 men) at Bohemia — the balance of forc…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 6478, own corps) vs Archduke Charles (lost 1999) — Reinforcements from Teulie bolstered Murat's position — though Davout never arrived, Sire. — The corps system brought Teulie in. — The Hofkriegsrat's orders reached Archduke John too late.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 3 actions unused) Turn 8 begins!
- enemy phase: 9 actions, 5 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · ArchdukeJohn strikes back after successfully defending! · Archduke Charles's forces press forward aggressively. Archduke Charles gains the advantage over Massena. Casualties: Ar… · Archduke John launches a decisive assault. Archduke John gains the advantage over Davout. Casualties: Archduke John 492…
  - 🏴 Austria: Casualties: Archduke John 2,083, Ney's army 5,869. Both armies remain in the field. Franconia has been captured by Austria!
  - 🏴 Austria: Both armies remain in the field. ArchdukeJohn advances into Tyrol. (211 lost to march) Tyrol has been captured by Austria!
  - 🏴 Bavaria: Deroy moves from Croatia to Carniola. Carniola falls to Bavaria!
  - 🏴 Bavaria: Deroy moves from Carniola to Bohemia. Bohemia falls to Bavaria!
  - 🏴 Bavaria: Deroy marches from Bohemia into Franconia unopposed! (61 lost to march — forward supply lines reduce losses) Captured: Austria → Bavaria
  - ⚔ Archduke Charles (lost 727, own corps) vs Bernadotte (lost 6715) — Where was Soult? Bernadotte held the field alone — reinforcement never came.
  - ⚔ Archduke John (lost 612, own corps) vs Ney (lost 1977, own corps) — Reinforcements from Davout and Napoleon bolstered Ney's position — though Soult never arrived, Sire. — Berthier: the corps marched apart and arrived together.
  - ⚔ Archduke Charles (lost 916) vs Massena (lost 10296, own corps) — Even the favorable ground could not save Massena, Sire. Archduke Charles overcame the terrain.
  - ⚔ Archduke John (lost 152, own corps) vs Davout (lost 3573) — Even the favorable ground could not save Davout, Sire. Archduke John overcame the terrain.
  - verbs: attack×5, move×3, unfortify×1
- LEDGER treasury 10404 · net +1411 · threat 80 · provinces 28 (+0) · ceiling 20061 · army 94653 · vassals Holland 91 · Kingdom of Italy 94 · Switzerland 89
  - NET income 2590 · trade 587 · admin 50 · tribute 698 · upkeep 720 · charges 1226 · contributions 110 · blockade 368 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover.
  - TURN EVENTS 11
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +4 medium/low (diplomatic_we_threshold, diplomatic_dp_regen, paymaster_subsidy, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 28 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✗ Davout is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Ney, fortify` → ✗ Ney is recovering from retreat and cannot fortify. Recovery: 2 turns remaining.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shift…
- CMD `Massena, move to Milan` → ✗ Massena is already in Milan.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 3 actions unused) Turn 9 begins!
- enemy phase: 6 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Tyrol into Bohemia unopposed! (931 lost to march) Captured: Bavaria → Austria · Archduke Charles delivers an effective strike. Archduke Charles gains the advantage over Deroy. Casualties: Archduke Ch…
  - 🏴 Austria: ArchdukeCharles marches from Tyrol into Bohemia unopposed! (931 lost to march) Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 1310) vs Deroy (lost 3485) — A standard affair. Nothing unusual to report.
  - verbs: attack×2, retreat×1, stance_change×1, wait×1, recruit×1
- LEDGER treasury 11844 · net +1198 · threat 78 · provinces 28 (+0) · ceiling 19868 · army 90869 · vassals Holland 91 · Kingdom of Italy 97 · Switzerland 88
  - NET income 2590 · trade 587 · admin 50 · tribute 703 · upkeep 696 · charges 1468 · contributions 110 · blockade 368 · admiralty 90
- DISPATCH: Sire — 3 turns now with enemy colours on French soil. The country is watching to see how long we permit it.
  - TURN EVENTS 8
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG sponsorship_granted: Russia sponsors Austria against France (300g/turn)

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Lannes, move to Bohemia` → ✗ Lannes is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `Murat, drill` → ✗ Murat cannot drill with enemy forces nearby! Archduke Charles is at Franconia, just one region away.
- CMD `recruit 10000 cavalry with Murat` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: 4 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles takes Franconia where he stands! Captured: Bavaria → Austria · Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Deroy. Casualties: Archduke Cha…
  - 🏴 Austria: ArchdukeCharles takes Franconia where he stands! Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 1222) vs Deroy (lost 4758) — Deroy held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: attack×2, wait×1, recruit×1
- LEDGER treasury 13038 · net +980 · threat 76 · provinces 28 (+0) · ceiling 19467 · army 86804 · vassals Holland 91 · Kingdom of Italy 100 · Switzerland 87
  - NET income 2590 · trade 587 · admin 50 · tribute 707 · upkeep 664 · charges 1682 · contributions 150 · blockade 368 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 7
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 16 approaches from Bavaria and Austria are rebuffed (open borders agreement)

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✗ Cannot move into Franconia - enemy forces present! Use ATTACK to engage Archduke Charles.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Milan. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifie…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Munich, Swabia.
  - saved `CMD-H_t10` → Game saved: CMD-H_t10
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 3 actions unused) Turn 11 begins!
- enemy phase: 5 actions, 2 attacks — Russia, Prussia, Spain and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles assaults the Munich garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 3,404 troops. G… · ArchdukeCharles assaults the Munich garrison! Garrison collapses (5,000 -> 0). ArchdukeCharles loses 1,872 troops in th…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -93g, Bavaria -125g. Captured: Bavaria → Austria
  - verbs: attack×2, naval_expedition×1, move×1, form_square×1
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 14055 · net +824 · threat 74 · provinces 28 (+0) · ceiling 19345 · army 83559 · vassals Holland 91 · Kingdom of Italy 100 · Switzerland 86
  - NET income 2590 · trade 587 · admin 50 · tribute 712 · upkeep 632 · charges 1875 · contributions 150 · blockade 368 · admiralty 90
- DISPATCH: Sire — Andalusia has been taken by Britain.
  - RAIL expedition_landed: THE LANDING: Wellesley has put 5,000 men ashore at Andalusia.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 2,126 gold. Prussia is now free to look elsewhere.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 5
- DIPLO +4 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift ×2)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: 14 approaches from Austria and Bavaria are rebuffed (open borders agreement)

## Turn 11 — Late February 1806
  - MAILBOX #10 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #11 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
- CMD `Ney, attack Archduke John` → ✗ Cannot attack Archduke John — armistice with Austria (5 turns remaining).
- CMD `Lannes, attack Archduke John` → ✗ Lannes is fortified at Swabia and cannot attack. Order 'unfortify' first to make the army mobile.
- CMD `Murat, move to Franconia` → ✗ Cannot enter Franconia — it is controlled by Austria (diplomatic state: ARMISTICE). Open borders or higher required.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 2 actions unused) Turn 12 begins!
- enemy phase: 3 actions, 1 attacks — Russia, Prussia, Spain and 4 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Munich into Swabia unopposed! (125 lost to march — forward supply lines reduce losses) Cap…
  - 🏴 Austria: ArchdukeCharles marches from Munich into Swabia unopposed! (125 lost to march — forward supply lines reduce losses) Captured: Bavaria → Austria
  - verbs: fortify×1, attack×1, break_square×1
- ENVOYS WAITING 2 · Naples open borders · Britain settlement offer
- LEDGER treasury 14950 · net +714 · threat 72 · provinces 28 (+0) · ceiling 19443 · army 79933 · vassals Holland 91 · Kingdom of Italy 95 · Switzerland 85
  - NET income 2590 · trade 524 · admin 50 · tribute 712 · upkeep 608 · charges 2056 · contributions 80 · blockade 328 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 6 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL nation_eliminated: Sire — Bavaria has been eliminated from the war.
  - RAIL diplomatic_ai_proposal: An envoy from Naples has arrived with a proposal.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 4
- DIPLO +5 medium/low (diplomatic_treaty_signed, law_enacted_abroad, diplomatic_dp_regen, diplomatic_vassal_contingent, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 400g reaches Austria
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven

## Turn 12 — Early March 1806
  - LETTER Naples: Open Borders Agreement → accept
  - MAILBOX #12 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #13 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #14 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Britain + Russia (4 pairs resolved). Status quo: Andalusia stays British by the treaty. → display-only
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 14. Ney's march to Franche-Comte is set aside.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- ORDER Bernadotte [completed]: Bernadotte arrives at Franche-Comte. Bernadotte: "Done, and done properly — no stragglers, no surprises."
- ORDER Lannes [error]: Lannes could not advance toward Franche-Comte.
- ORDER Murat [completed]: Murat arrives at Franche-Comte. Murat: "It is done. Point me at something that shoots back, Sire."
- ORDER Napoleon [completed]: Napoleon arrives at Franche-Comte.
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 17765 · net +2531 · threat 38 · provinces 28 (+0) · ceiling 67972 · army 78155 · vassals Holland 89 · Kingdom of Italy 96 · Switzerland 84
  - NET income 2590 · trade 573 · admin 50 · tribute 712 · upkeep 600 · charges 794
- DISPATCH: Sire — under the peace with Austria. Ney is on the wrong side of the frontier at Swabia, Sire — the ground changed hands under him. Berthier has put him on the road home to Franche-Comte; he has 4 tu…
  - RAIL settlement_summary: Settlement of France vs Britain + Russia: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 6
- COURTS: The court of Britain eases over The Low Countries — service to the strong is now the length of its tether.
- COURTS: The court of Austria eases over Redeem Italy — alliance is now the length of its tether.
- COURTS: And Sardinia stirs at its own design.
- DIPLO +8 medium/low (diplomatic_treaty_signed, diplomatic_coalition_dissolved, diplomatic_dp_regen, diplomatic_vassal_contingent, blockade_broken ×3, agenda_shift)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Russia has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 72 to 36.
  - LOG nation_eliminated: Bavaria has been eliminated from the war.

## Turn 13 — Late March 1806
  - MAILBOX #13 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #15 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (89 → 99); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✗ Cannot attack Archduke John — armistice with Austria (3 turns remaining).
- CMD `Davout, move to Franconia` → ✗ Cannot enter Franconia — the evacuation corridor with Austria grants safe passage HOME to stranded corps, not entry. Davout can already reach the body of the realm from …
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 4 actions unused) Turn 14 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- ORDER Lannes [error]: Lannes could not advance toward Franche-Comte.
- LEDGER treasury 19975 · net +2099 · threat 40 · provinces 28 (+0) · ceiling 61603 · army 76463 · vassals Holland 98 · Kingdom of Italy 97 · Switzerland 83
  - NET income 2590 · trade 573 · admin 50 · tribute 375 · upkeep 584 · charges 905
- DISPATCH: DRILL COMPLETE: Ney's training is finished! +20% attack bonus ready for next battle. The ranks steady with the work: morale +10 (now 10).
  - TURN EVENTS 5
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as an ultimatum.
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)
  - LOG sponsorship_expired: The compact between Britain and Sweden lapses

## Turn 14 — Early April 1806
- CMD `Lannes, fortify` → ✗ Lannes is already fortified at Swabia (+2% defense).
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Swa…
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Milan and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 2 actions unused) Turn 15 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×2
- ORDER Lannes [error]: Lannes could not advance toward Franche-Comte.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- LEDGER treasury 22090 · net +2233 · threat 42 · provinces 28 (+0) · ceiling 66384 · army 74772 · vassals Holland 97 · Kingdom of Italy 98 · Switzerland 82
  - NET income 2590 · trade 573 · admin 50 · tribute 600 · upkeep 568 · charges 1012
- DISPATCH: Sire — Russia moves toward war with Sweden. The design is open; the timing is not.
  - RAIL crisis_brewing: THE BREWING CRISIS: Russia will move on Sweden. You may compensate (1,200g — you can afford it); guarantee Sweden (1 DP — 7 in hand); or let the war …
  - TURN EVENTS 7
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)

## Turn 15 — Late April 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Swabia. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Milan. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, garrison×1
- ORDER Lannes [error]: Lannes could not advance toward Franche-Comte.
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 23812 · net +1525 · threat 44 · provinces 28 (+0) · ceiling 43666 · army 73126 · vassals Holland 96 · Kingdom of Italy 99 · Switzerland 81
  - NET income 2590 · trade 573 · admin 50 · tribute 600 · upkeep 560 · charges 1675 · requisitions 37 · admiralty 90
- DISPATCH: Sire — Russia moves toward war with Sweden. The design is open; the timing is not.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - RAIL diplomatic_armistice_expired_war: The armistice between Austria and France has collapsed. War resumes!
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 6
- COURTS: The court of Britain hardens over The Low Countries — prepared now to go as far as an ultimatum.
- COURTS: The court of Austria hardens over Redeem Italy — prepared now to go as far as war.
- COURTS: And Sardinia stirs at its own design.
- DIPLO +2 medium/low (diplomatic_dp_regen, coercive_demand)

## Turn 16 — Early May 1806
  - MAILBOX #14 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #16 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (81 → 91); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, move to Bohemia` → ✗ Cannot advance while engaged with Archduke Charles at Swabia. He may fall back to friendly ground — Rhineland, Lorraine, Franche-Comte — or fight.
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke Charles at …
  - POPUP objection: Murat, Murat firmly objects: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke Charles at Swabia instead.) → trust
  - ↳ MUSTER — Murat (8,729; expect about 42,570 with the corps likely to arrive, up to 46,142 if all march) vs Archduke Charles (25,894 men) at Swabia — the balance of force looks even — a hard fight that may go against us.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 1294, own corps) vs Archduke Charles (lost 3428, own corps) — Napoleon reached the field beside Murat, Sire — it saved the line, no more.
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 2 actions unused) Turn 17 begins!
- enemy phase: 7 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack faces a difficult fight. Ney holds the line. Casualties: Mack 3,319, Ney's army 1,470. Both armies remain in the f…
  - ⚔ Mack (lost 3319) vs Ney (lost 346, own corps) — Ney fought without Bernadotte's support. The roads, or the will, proved insufficient.
  - verbs: move×2, recruit×2, retreat×1, stance_change×1, attack×1
- ORDER Lannes [completed]: Lannes arrives at Franche-Comte. Lannes: "Done — and I trust the next order has more fire in it."
- ORDER Ney [awaiting_response]: Ney is cornered at Swabia with 3,743 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
  - POPUP strategic_interrupt: Ney, last_stand, Ney is cornered at Swabia with 3,743 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ The moment has passed — the quarrel between Bernadotte and Ney no longer waits on the council — one of them h…
- LEDGER treasury 24818 · net +1149 · threat 45 · provinces 28 (+0) · ceiling 38622 · army 63092 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 92
  - NET income 2590 · trade 573 · admin 50 · tribute 375 · upkeep 488 · charges 1898 · requisitions 37 · admiralty 90
- DISPATCH: Sire — Russia has declared war on Sweden. The stated cause: The Gulf and the Straits.
  - RAIL broken_bargain: The compact with Sweden lies torn — Russia is named the breaker in every chancery of Europe.
  - TURN EVENTS 9
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as war.
- DIPLO +4 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade, blockade_begins, diplomatic_relation_shift)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Milan. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifie…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franche-Comte. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Milan (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 2 actions unused) Turn 18 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Mack engages in solid combat. Soult holds the line. Casualties: Mack 5,391, Soult's army 958. Both armies remain in the…
  - ⚔ Mack (lost 5391) vs Soult (lost 634, own corps) — Reinforcements! Murat, Bernadotte and Napoleon marched onto the field beside Soult. The enemy's advantage melted away.
  - verbs: fortify×1, attack×1
- LEDGER treasury 25939 · net +994 · threat 45 · provinces 28 (+0) · ceiling 37380 · army 61212 · vassals Holland 96 · Kingdom of Italy 100 · Switzerland 93
  - NET income 2590 · trade 573 · admin 50 · tribute 375 · upkeep 464 · charges 2077 · requisitions 37 · admiralty 90
- DISPATCH: Sire — Marshal Ney has been taken. Austria holds him prisoner.
  - TURN EVENTS 10
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_we_threshold, diplomatic_dp_regen, diplomatic_vassal_contingent)

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Milan, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, form_square×1, recruit×1
- LEDGER treasury 26949 · net +842 · threat 45 · provinces 28 (+0) · ceiling 36300 · army 60316 · vassals Holland 95 · Kingdom of Italy 100 · Switzerland 93
  - NET income 2590 · trade 573 · admin 50 · tribute 375 · upkeep 448 · charges 2245 · requisitions 37 · admiralty 90
- DISPATCH: Soult's fortifications strengthen: +11% defense (max 12%)
  - RAIL design_promoted: REVANCHE: Sweden will not forgive Russia the loss of Karelia. A new design hardens in their court.
  - TURN EVENTS 6
- DIPLO +3 medium/low (diplomatic_dp_regen, diplomatic_ai_ai_treaty, agenda_shift)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sardinia and Austria (Defensive Alliance)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✗ Cannot move into Franconia - enemy forces present! Use ATTACK to engage Archduke Charles, Archduke John.
- CMD `Murat, drill` → ✗ Murat cannot drill with enemy forces nearby! Archduke Charles is at Franconia, just one region away.
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 4 actions unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 27791 · net +684 · threat 45 · provinces 28 (+0) · ceiling 35122 · army 59447 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 93
  - NET income 2590 · trade 573 · admin 50 · tribute 375 · upkeep 448 · charges 2403 · requisitions 37 · admiralty 90
- DISPATCH: Soult's fortifications decay: 11% → 10%
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG design_promoted: REVANCHE: Sweden swears to retake Karelia — Russia is not forgiven

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+10% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
  - saved `CMD-H_t20` → Game saved: CMD-H_t20
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 4 actions, 3 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles launches a decisive assault. Brutal stalemate between Archduke Charles and Soult. Heavy casualties on … · Archduke Charles launches a decisive assault. Brutal stalemate between Archduke Charles and Napoleon. Heavy casualties … · Mack's forces advance steadily. Soult holds the line. Casualties: Mack 2,844, Soult 1,394. Both armies remain in the fi…
  - 🏴 Austria: [!] MARSHAL CAPTURED — Bernadotte is taken by Austria at Swabia!
  - ⚔ Archduke Charles (lost 2145, own corps) vs Soult (lost 1200, own corps) — Lannes reached the field beside Soult, Sire — it saved the line, no more.
  - ⚔ Archduke Charles (lost 1403) vs Napoleon (lost 509, own corps) — Neither Napoleon nor Archduke Charles could claim the field. The armies remain locked.
  - ⚔ Mack (lost 2844) vs Soult (lost 1394) — A wise investment in fortification. Soult's position was impregnable to Mack's assault.
  - verbs: attack×3, unfortify×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Lannes seeks an audience → acknowledge
  -     ↳ Lannes's grievance runs its course.
- LEDGER treasury 28223 · net +895 · threat 45 · provinces 28 (+0) · ceiling 37241 · army 50247 · vassals Holland 94 · Kingdom of Italy 100 · Switzerland 94
  - NET income 2590 · trade 573 · admin 50 · tribute 712 · upkeep 376 · charges 2601 · requisitions 37 · admiralty 90
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - TURN EVENTS 10
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Milan. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (His loyalty is frayed by neglect — his victories remain unrewarded.) (Trust him and he will …
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (His loyalty is frayed by neglect — his victories remain unrewarded.) (Trust him and he will attack Archduke Charles at Swabia instead.) → trust
  - ↳ MUSTER — Lannes (7,847) vs Archduke Charles (20,512 men) at Swabia — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 3346) vs Archduke Charles (lost 737, own corps) — Lannes's army has been badly mauled. Archduke Charles proved the stronger force today.
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Lorraine (field levy — no depot; capped at 3,000) (recruitment is drafted in fixe…
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 actions unused) Turn 22 begins!
- SPENT 1035g on this turn's orders
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending!
  - ⚔ Archduke Charles (lost 286) vs Napoleon (lost 1051, own corps) — Napoleon's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×1, form_square×1
- ORDER Lannes [awaiting_response]: Lannes is cornered at Franche-Comte with 2,899 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout.
- ORDER Napoleon [awaiting_response]: Napoleon's Guard is SPENT at Franche-Comte — 1,167 men cannot buy another road, Sire. Fight to the last, or cut our way out.
  - POPUP strategic_interrupt: Lannes, last_stand, Lannes is cornered at Franche-Comte with 2,899 men, Sire — capture looms. He asks leave to fight to the last, or he can attempt a breakout. → fight_to_the_last
  - POPUP strategic_interrupt: Napoleon, last_stand, Napoleon's Guard is SPENT at Franche-Comte — 1,167 men cannot buy another road, Sire. Fight to the last, or cut our way out. → fight_to_the_last
- ENVOYS WAITING 2 · Austria armistice losing · Holland client petition
- LEDGER treasury 26922 · net -500 · threat 45 · provinces 28 (+0) · ceiling 23744 · army 43182 · vassals Holland 89 · Kingdom of Italy 99 · Switzerland 90
  - NET income 2583 · trade 573 · admin 50 · tribute 712 · upkeep 328 · charges 3927 · contributions 73 · admiralty 90
- DISPATCH: Sire — Soult, crowned two turns ago, has been driven back.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 11
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)

## Turn 22 — Early August 1806
  - MAILBOX #15 Austria incoming_proposal: Austria — Armistice → activated
  - MAILBOX #16 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #17 → accept
  -     ↳ refused: Sire, another matter has arrived since — this concerns Holland. Your earlier answer was not delivered; the ma…
  - POPUP diplomatic_dialogue: incoming_proposal #18 → grant the petition
  - POPUP diplomatic_dialogue: Austria, armistice_losing #17 → accept
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (89 → 99); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
  - POPUP diplomatic_dialogue: Holland, client_petition #18 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Lorraine. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat is recovering from retreat and cannot fortify. Recovery: 1 turn remaining.
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 actions unused) Turn 23 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, break_square×1, recruit×1, grant_dotation×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- LEDGER treasury 28184 · net +1161 · threat 45 · provinces 28 (+0) · ceiling 42687 · army 43182 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2585 · trade 573 · admin 50 · tribute 375 · upkeep 328 · charges 2094
- DISPATCH: Sire — the Emperor himself is TAKEN. Austria holds him, and the Empire holds its breath.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - TURN EVENTS 6
- COURTS: The court of Britain eases over The Low Countries — service to the strong is now the length of its tether.
- COURTS: The court of Austria eases over Redeem Italy — alliance is now the length of its tether.
- COURTS: And Sardinia stirs at its own design.
- DIPLO +3 medium/low (diplomatic_treaty_signed, diplomatic_dp_regen, diplomatic_vassal_contingent)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (defensive alliance)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Milan. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifie…
- CMD `Lannes, unfortify` → ✗ Marshal Lannes is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Soult, drill` → ✗ Soult is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 3 actions unused) Turn 24 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
- LEDGER treasury 29346 · net +1294 · threat 45 · provinces 28 (+0) · ceiling 45512 · army 43182 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2586 · trade 573 · admin 50 · tribute 600 · upkeep 328 · charges 2187
- DISPATCH: Sire — 7 turns without settlement on Marshal Soult. A rente would close it today; the arrears will not close themselves.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Lorraine. Troops will be locked in training next turn, bonus ready turn 26.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 170 gold (Soult's intendance: -15%). Morale: 13% -> 18%
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 2 actions unused) Turn 25 begins!
- SPENT 170g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
  -     ↳ Massena's grievance runs its course.
- LEDGER treasury 30436 · net +1185 · threat 45 · provinces 28 (+0) · ceiling 45237 · army 46182 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2588 · trade 573 · admin 50 · tribute 600 · upkeep 352 · charges 2274
- DISPATCH: Sire — Marshal Soult's claim is 8 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✗ Marshal Lannes is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 3 actions unused) Turn 26 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 31623 · net +1092 · threat 45 · provinces 28 (+0) · ceiling 45262 · army 46182 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 573 · admin 50 · tribute 600 · upkeep 352 · charges 2369
- DISPATCH: Sire — Marshal Soult's claim is 9 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Marshal Ney is a prisoner of Austria, Sire — no order can reach him until his release.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 33989 · net +2290 · threat 45 · provinces 28 (+0) · ceiling 105531 · army 66182 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 585 · admin 50 · tribute 600 · upkeep 512 · charges 1023
- DISPATCH: Sire — the Emperor's star dims. The Presence that gave his corps +10% on the field gives +5% this morning; the courts have begun to notice that he can be beaten.
  - RAIL diplomatic_armistice_expired_peace: The armistice between Austria and France has concluded. Peace declared.
  - TURN EVENTS 2
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Milan. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Lorraine. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 10,000 infantry at Paris - Cost: 150 gold (capital discount). Morale: 50% -> 43%
- CMD `end turn` → ✓ Turn 27 ended. Turn 28 begins!
- SPENT 150g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 36061 · net +2176 · threat 45 · provinces 28 (+0) · ceiling 104031 · army 75282 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 585 · admin 50 · tribute 600 · upkeep 560 · charges 1089
- DISPATCH: Sire — Marshal Soult's claim is 11 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 8
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 1 action unused) Turn 29 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 38237 · net +2106 · threat 45 · provinces 28 (+0) · ceiling 104031 · army 74411 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 585 · admin 50 · tribute 600 · upkeep 560 · charges 1159
- DISPATCH: Sire — Marshal Soult's claim is 12 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (defensive alliance)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Milan. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifie…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Paris. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Lorraine. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot sh…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- LEDGER treasury 40351 · net +2383 · threat 45 · provinces 28 (+0) · ceiling 114812 · army 73565 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 585 · admin 50 · tribute 937 · upkeep 552 · charges 1227
- DISPATCH: Sire — Marshal Soult's claim is 13 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 6
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat is fortified and cannot drill. Abandon fortification first.
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Milan, Your Majesty. Recruitment is impossible there.'
  - saved `CMD-H_t30` → Game saved: CMD-H_t30
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- LEDGER treasury 42734 · net +2307 · threat 45 · provinces 28 (+0) · ceiling 114812 · army 72747 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 585 · admin 50 · tribute 937 · upkeep 552 · charges 1303
- DISPATCH: Sire — Marshal Soult's claim is 14 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 7
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Par…
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. Turn 32 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 45049 · net +2241 · threat 45 · provinces 28 (+0) · ceiling 115062 · army 71953 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 585 · admin 50 · tribute 937 · upkeep 544 · charges 1377
- DISPATCH: Sire — Marshal Soult's claim is 15 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 6
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Paris. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 actions unused) Turn 33 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- LEDGER treasury 47290 · net +2169 · threat 45 · provinces 28 (+0) · ceiling 115062 · army 71183 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 585 · admin 50 · tribute 937 · upkeep 544 · charges 1449
- DISPATCH: Sire — Marshal Soult's claim is 16 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Milan. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Paris. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Canno…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Lorraine. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✓ Berthier notes: 'Marshal Murat commands cavalry, Sire.' Murat recruits 3,000 cavalry at Lorraine (field levy — no depot; capped at 3,000) (recruitment is drafted in fixe…
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 1 action unused) Turn 34 begins!
- SPENT 345g on this turn's orders
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- LEDGER treasury 49076 · net +2088 · threat 45 · provinces 28 (+0) · ceiling 114312 · army 73434 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 585 · admin 50 · tribute 937 · upkeep 568 · charges 1506
- DISPATCH: Sire — Marshal Soult's claim is 17 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Milan. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 actions unused) Turn 35 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 51146 · net +2004 · threat 45 · provinces 28 (+0) · ceiling 113750 · army 72708 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 535 · admin 50 · tribute 937 · upkeep 536 · charges 1572
- DISPATCH: Sire — Marshal Soult's claim is 18 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Milan. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifie…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Paris. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Lorraine. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot sh…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action unused) Turn 36 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- LEDGER treasury 53150 · net +1940 · threat 45 · provinces 28 (+0) · ceiling 113750 · army 72005 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 535 · admin 50 · tribute 937 · upkeep 536 · charges 1636
- DISPATCH: Sire — Marshal Soult's claim is 19 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Paris. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot move…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Milan. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 200 gold. Morale: 38% -> 38%
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 2 actions unused) Turn 37 begins!
- SPENT 200g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- LEDGER treasury 54847 · net +1861 · threat 45 · provinces 28 (+0) · ceiling 113000 · army 74321 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 535 · admin 50 · tribute 937 · upkeep 560 · charges 1691
- DISPATCH: Sire — Marshal Soult's claim is 20 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Lorraine. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 2 actions unused) Turn 38 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 56716 · net +1810 · threat 45 · provinces 28 (+0) · ceiling 113250 · army 73660 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 535 · admin 50 · tribute 937 · upkeep 552 · charges 1750
- DISPATCH: Sire — Marshal Soult's claim is 21 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 5
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Paris. Army is now mobile.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 3 actions unused) Turn 39 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1
- LEDGER treasury 58526 · net +1752 · threat 45 · provinces 28 (+0) · ceiling 113250 · army 73017 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 535 · admin 50 · tribute 937 · upkeep 552 · charges 1808
- DISPATCH: Sire — Marshal Soult's claim is 22 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Milan. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Lorraine. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 10,000 infantry at Paris - Cost: 150 gold (capital discount). Morale: 63% -> 51%
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 2 actions unused) Turn 40 begins!
- SPENT 150g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 60035 · net +1631 · threat 45 · provinces 28 (+0) · ceiling 111000 · army 82093 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 535 · admin 50 · tribute 937 · upkeep 624 · charges 1857
- DISPATCH: Sire — Marshal Soult's claim is 23 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- COURTS: The court of Russia eases over The Gulf and the Straits — alliance is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Paris. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Milan (+2% defense).
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
  - saved `CMD-H_t40` → Game saved: CMD-H_t40
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 actions unused) Turn 41 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 6 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 61666 · net +1579 · threat 49 · provinces 28 (+0) · ceiling 111000 · army 81196 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 90
  - NET income 2590 · trade 535 · admin 50 · tribute 937 · upkeep 624 · charges 1909
- DISPATCH: Sire — Marshal Soult's claim is 24 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_armed_peace_fuse: THE ARMED PEACE: 20 turns without a French battle — the courts re-arm. Europe's alarm rises 3 a turn toward the league gate at 60; Britain, Russia, A…
  - TURN EVENTS 4
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Austria (defensive alliance)

---
finished: **completed** · commands 200 · popups 56 · battles 27
