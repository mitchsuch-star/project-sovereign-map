# Playtest digest — CMDR-H

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first", "client_petition": "refuse"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `c14678984809` (dirty) · content `d4a1fdd2fc4f` · driver `e498338939cb`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 108,125 with the corps likely to arrive, up to 114,642 if all march) vs Mack (large force) at Swabia — the balance of force looks favo…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1847, own corps) vs Mack (lost 24408) — Reinforcements from Davout, Lannes, Murat and Napoleon bolstered Ney's position — though Soult and Bernadotte never arr… — The corps system brought Murat in. — Berthier: the corps marched apart and arrived together.
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles engages in solid combat. Archduke Charles gains the advantage over Massena. Casualties: Archduke Charl… · Deroy delivers an effective strike. Deroy gains the advantage over Mack. Casualties: Deroy 983, Mack 8,861. Both armies…
  - ⚔ Archduke Charles (lost 3964) vs Massena (lost 6353) — The margin was slim. Training and preparation would serve Massena well.
  - ⚔ Deroy (lost 983) vs Mack (lost 8861) — Mack stood alone, Sire. Archduke John never came.
  - verbs: attack×2, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1651 · net +1439 · threat 76 · provinces 28 · ceiling 32747 · army 174609 · vassals Holland 99 · Kingdom of Italy 100 · Switzerland 97
  - NET income 2590 · trade 400 · admin 50 · tribute 895 · upkeep 2156 · blockade 250 · admiralty 90
- DISPATCH: Sire — Marshal Ney holds the field at Swabia — Mack's corps is broken and flees.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +9 medium/low (diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_contingent ×2, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ Ney pursues Mack (at Tyrol). Moves to Franconia. A standing order, not a single attack: he closes 1 province a turn, attacks on arrival, may be diverted by an interrupt,…
- CMD `Davout, attack Mack` → ✓ Davout pursues Mack (at Tyrol). Moves to Franconia. A standing order, not a single attack: he closes 1 province a turn, attacks on arrival, may be diverted by an interru…
- CMD `Soult, move to Alsace` → ✗ Not enough actions! Need 1, have 0 — Soult cannot march to Alsace today.
- CMD `Murat, move to Franche-Comte` → ✗ Not enough actions! Need 1, have 0 — Murat cannot march to Franche-Comte today.
- CMD `end turn` → ✓ Turn 2 ended. Turn 3 begins!
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles's forces press forward aggressively. Brutal stalemate between Archduke Charles and Massena. Heavy casu… · Archduke Charles engages in solid combat. Archduke Charles gains the advantage over Teulie. Casualties: Archduke Charle…
  - ⚔ Archduke Charles (lost 4330) vs Massena (lost 4342, own corps) — An inconclusive affair. Both sides bloodied but unbroken. — The Hofkriegsrat's orders reached Archduke John too late.
  - ⚔ Archduke Charles (lost 2676) vs Teulie (lost 1357, own corps) — A grievous defeat for Teulie, Sire. The losses are severe.
  - verbs: attack×2, wait×1
- ORDER Davout [active]: Davout is pursuing Mack (0 turns remaining).
- ORDER Ney [active]: Ney is pursuing Mack (0 turns remaining).
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 2908 · net +1641 · threat 74 · provinces 28 (+0) · ceiling 31580 · army 164669 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 93
  - NET income 2590 · trade 450 · admin 50 · tribute 829 · upkeep 1856 · charges 51 · blockade 281 · admiralty 90
- DISPATCH: Sire — London now pays Vienna 200 gold a turn against us — her war with us is paid for.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +6 medium/low (diplomatic_treaty_signed ×3, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 29 approaches from Prussia, Bavaria and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Hanover rebuffs Prussia (design ask)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (20,407; expect about 47,322 with the corps likely to arrive, up to 47,970 if all march) vs Mack (substantial force) at Bohemia — the balance of force looks…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 299, own corps) vs Mack (lost 15770) — Davout arrived to reinforce Ney! The timely arrival swung the battle in our favor, Sire. And Mack was taken on that fie…
  - POPUP capture_choice[capture]: Bohemia, Ney → secure
- CMD `Davout, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Rhineland to Swabia (169 lost to march)
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 741 gold (×3 at war) (×1.24 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 2 actions unused) Turn 4 begins!
- SPENT 741g on this turn's orders
- enemy phase: 3 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke Charles struggles in a costly engagement. Brutal stalemate between Archduke Charles and Massena. Heavy casualt… · Archduke Charles's attack meets fierce resistance. Archduke Charles gains the advantage over Teulie. Casualties: Archdu…
  - ⚔ Archduke Charles (lost 3013) vs Massena (lost 3743, own corps) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - ⚔ Archduke Charles (lost 1757) vs Teulie (lost 1200, own corps) — Teulie's army has been badly mauled. Archduke Charles proved the stronger force today.
  - verbs: attack×2, wait×1
- ORDER Davout [active]: Davout answered the guns this turn and stands at Bohemia; the pursuit resumes next turn.
  - POPUP marshal_audience: jealousy_confrontation, Marshal Davout seeks an audience → acknowledge
  -     ↳ Davout's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 3614 · net +1697 · threat 82 · provinces 29 (+1) · ceiling 21142 · army 158721 · vassals Holland 96 · Kingdom of Italy 95 · Switzerland 90
  - NET income 2636 · trade 525 · admin 50 · tribute 799 · upkeep 1668 · charges 156 · occupation 70 · blockade 329 · admiralty 90
- DISPATCH: Sire — General Mack of Austria is taken at Bohemia — he is our prisoner, and their order of battle is one commander shorter.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - TURN EVENTS 7
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as an ultimatum.
- DIPLO +3 medium/low (diplomatic_treaty_signed ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Naples and Bavaria rebuff Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `Ney, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Bohemia. Defense bonus: +7% (grows +3% per turn, m…
- CMD `Massena, move to Tyrol` → ✗ Cannot move into Tyrol - enemy forces present! Use ATTACK to engage Archduke Charles, Archduke John.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. (Warning: 2 actions unused) Turn 5 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, wait×1, recruit×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Bernadotte seeks an audience → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 5471 · net +1571 · threat 80 · provinces 29 (+0) · ceiling 21180 · army 157806 · vassals Holland 96 · Kingdom of Italy 97 · Switzerland 88
  - NET income 2637 · trade 587 · admin 50 · tribute 802 · upkeep 1630 · charges 347 · occupation 70 · blockade 368 · admiralty 90
- DISPATCH: Sire — St Petersburg now pays London 300 gold a turn against us — her war with us is paid for.
  - RAIL crisis_brewing: THE BREWING CRISIS: Prussia will move on Hanover. You may compensate (1,200g — you can afford it); guarantee Hanover (1 DP — 7 in hand); or let the w…
  - TURN EVENTS 7
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)

## Turn 5 — Late November 1805
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (19,903; expect about 35,414 with the corps likely to arrive, up to 36,150 if all march) vs Archduke Charles (substantial force) at Tyrol — the balance of f…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 4215, own corps) vs Archduke Charles (lost 1737, own corps) — The reinforcement arrived, Sire. The verdict of the field went against us regardless.
- CMD `Lannes, attack Mack` → ✗ Mack is our prisoner at Paris, Sire — he leads no army. Hold him for the peace table.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (990 lost to march)
- CMD `Murat, move to Swabia` → ✗ Murat is already in Swabia.
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 2 actions unused) Turn 6 begins!
- enemy phase: 8 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Archduke John engages in solid combat. Archduke John gains the advantage over Teulie. Casualties: Archduke John 159, Te… · ArchdukeJohn assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeJohn loses 2,799 troops. Garrison… · ArchdukeJohn assaults the Milan garrison! Garrison collapses (5,000 -> 0). ArchdukeJohn loses 1,653 troops in the assau… · Deroy launches a decisive assault. Brutal stalemate between Deroy and Archduke John. Heavy casualties on both sides: De…
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -82g, Kingdom of Italy -125g. Captured: KingdomOfItaly → Austria
  - ⚔ Archduke John (lost 159) vs Teulie (lost 1635) — A grievous defeat for Teulie, Sire. The losses are severe.
  - ⚔ Deroy (lost 2083) vs Archduke John (lost 1858) — Neither Archduke John nor Deroy could claim the field. The armies remain locked.
  - verbs: attack×4, unfortify×1, move×1, wait×1, recruit×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 7056 · net +1857 · threat 78 · provinces 29 (+0) · ceiling 29918 · army 147272 · vassals Holland 92 · Kingdom of Italy 89 · Switzerland 82
  - NET income 2734 · trade 587 · admin 50 · tribute 712 · upkeep 1318 · charges 410 · occupation 40 · blockade 368 · admiralty 90
- DISPATCH: Sire — Ney, crowned three turns ago, has been beaten in the field.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 8
- DIPLO +5 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy, coercive_demand)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 6 — Early December 1805
  - MAILBOX #8 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #9 → refuse the petition
  - POPUP proposal_result: Switzerland's petition for relief is refused: loyalty −10 (82 → 72); bond 0 → -20 (-1 a turn). Nothing is charged. → display-only
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Archduke Charles is at Tyrol, just one region away.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archd…
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke John at Munich instead.) → trust
  - ↳ MUSTER — Lannes (15,578; expect about 52,635 with the corps likely to arrive, up to 53,203 if all march) vs Archduke John (10,236 men) at Munich — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 546, own corps) vs Archduke John (lost 7017) — Murat, Bernadotte and Napoleon arrived to reinforce Lannes, but Soult failed to reach the field in time. — Berthier: the corps marched apart and arrived together.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 3 actions unused) Turn 7 begins!
- enemy phase: 7 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — Deroy's forces advance steadily. Archduke Charles holds the line. Casualties: Deroy 4,297, Archduke Charles 1,317. Both…
  - ⚔ Deroy (lost 4297) vs Archduke Charles (lost 1317) — The square held its ground. Archduke Charles's infantry stood like a fortress on the field.
  - verbs: wait×2, recruit×2, unfortify×1, form_square×1, attack×1
  - ⚡ AUTONOMOUS: [Shield] Archduke Charles steps forward to cover Archduke John's retreat! "Archduke John is in no condition to fight - I'll handle this!"
  - ⚔ Murat (lost 2670, own corps) vs Archduke Charles (lost 4180) — Ney, Davout and Lannes arrived in time to steady Murat's position. The field was held, nothing further. — Berthier: the corps marched apart and arrived together.
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Bernadotte and Ney: They settle into cold war.
- LEDGER treasury 8542 · net +1620 · threat 79 · provinces 29 (+0) · ceiling 22219 · army 137798 · vassals Holland 93 · Kingdom of Italy 90 · Switzerland 70
  - NET income 2737 · trade 587 · admin 50 · tribute 712 · upkeep 1084 · charges 774 · contributions 110 · occupation 40 · blockade 368 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Gascony. No French corps stands in his path.
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover.
  - TURN EVENTS 11
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +4 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Switzerland rebuffs Prussia (defensive alliance)
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 6 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (15,688; expect about 50,310 with the corps likely to arrive, up to 53,063 if all march) vs Archduke Charles (25,751 men) at Tyrol — the balance of force lo…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1649, own corps) vs Archduke Charles (lost 3641) — Davout, Lannes and Napoleon arrived in time to steady Ney's position. The field was held, nothing further. — Berthier: the corps marched apart and arrived together.
- CMD `Davout, move to Bohemia` → ✗ Davout is already in Bohemia.
- CMD `Murat, attack Archduke Charles` → ✓ MUSTER — Murat (15,643) vs Archduke Charles (22,110 men) at Tyrol — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Murat (lost 4950) vs Archduke Charles (lost 685) — Ney reached Murat in time, Sire — but even together, the field could not be held.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 2 actions unused) Turn 8 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending!
  - 🏴 Bavaria: Deroy moves from Franconia to Tyrol. Tyrol falls to Bavaria!
  - ⚔ Archduke Charles (lost 1958) vs Davout (lost 1889) — Neither Davout nor Archduke Charles could claim the field. The armies remain locked.
  - verbs: attack×1, garrison×1, move×1
- LEDGER treasury 9754 · net +1500 · threat 77 · provinces 29 (+0) · ceiling 21394 · army 125383 · vassals Holland 91 · Kingdom of Italy 88 · Switzerland 65
  - NET income 2725 · trade 587 · admin 50 · tribute 712 · upkeep 968 · charges 998 · contributions 110 · occupation 40 · blockade 368 · admiralty 90
- DISPATCH: Sire — Ney, crowned five turns ago, has been beaten in the field.
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 10
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✓ Davout notes the risks but prepares the attack. MUSTER — Davout (18,308) vs Archduke Charles (substantial force) at Carniola — the balance of force looks unfavorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 3573) vs Archduke Charles (lost 820) — Geography was our enemy today, Sire. Archduke Charles held the superior ground.
- CMD `Ney, fortify` → ✗ Ney is recovering from retreat and cannot fortify. Recovery: 2 turns remaining.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shift…
- CMD `Massena, move to Milan` → ✓ Massena begins marching to Milan (distance: 2). Moved to Tyrol. Route: Tyrol -> Milan.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 1 action unused) Turn 9 begins!
- enemy phase: 3 actions, 1 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Carniola into Bohemia unopposed! (475 lost to march) Captured: France → Austria
  - 🏴 Austria: ArchdukeCharles marches from Carniola into Bohemia unopposed! (475 lost to march) Captured: France → Austria
  - verbs: attack×1, fortify×1, wait×1
- ORDER Massena [active]: Massena is marching to Milan (2 turns remaining).
  - POPUP marshal_petition: jealousy_confrontation, Marshal Bernadotte demands to be heard → acknowledge
  -     ↳ Bernadotte's grievance runs its course.
- LEDGER treasury 11019 · net +1224 · threat 75 · provinces 28 (-1) · ceiling 20069 · army 119616 · vassals Holland 89 · Kingdom of Italy 86 · Switzerland 60
  - NET income 2590 · trade 587 · admin 50 · tribute 712 · upkeep 928 · charges 1219 · contributions 110 · blockade 368 · admiralty 90
- DISPATCH: Sire — Davout's corps has been broken at Bohemia. He must reform before he fights again.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 8
- DIPLO +5 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 7 approaches from Austria, Prussia and Bavaria are rebuffed (open borders agreement)

## Turn 9 — Late January 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Lannes, move to Bohemia` → ✗ Cannot move into Bohemia - enemy forces present! Use ATTACK to engage Archduke Charles, Archduke John.
- CMD `Murat, drill` → ✗ Murat is recovering from retreat and cannot drill. Recovery: 1 turn remaining.
- CMD `recruit 10000 cavalry with Murat` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 4 actions unused) Turn 10 begins!
- enemy phase: 5 actions, 3 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles marches from Bohemia into Carniola unopposed! (532 lost to march) Captured: Bavaria → Austria · Archduke Charles launches a decisive assault. Archduke Charles gains the advantage over Deroy. Casualties: Archduke Cha… · ArchdukeCharles holds them at Croatia while allies attack from Carniola! (+1 coordination)
  - 🏴 Austria: ArchdukeCharles marches from Bohemia into Carniola unopposed! (532 lost to march) Captured: Bavaria → Austria
  - ⚔ Archduke Charles (lost 1512) vs Deroy (lost 2937) — Deroy held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - ⚔ Archduke Charles (lost 1052) vs Deroy (lost 2535) — Even the favorable ground could not save Deroy, Sire. Archduke Charles overcame the terrain.
  - verbs: attack×3, move×1, unfortify×1
- ORDER Massena [continues]: Massena hears cannon fire at Croatia but cannot answer it — Cannot move into Carniola - enemy forces present! Use ATTACK to engage Archduke John. His…
- LEDGER treasury 12227 · net +1012 · threat 73 · provinces 28 (+0) · ceiling 19536 · army 118214 · vassals Holland 89 · Kingdom of Italy 86 · Switzerland 57
  - NET income 2590 · trade 587 · admin 50 · tribute 712 · upkeep 904 · charges 1415 · contributions 150 · blockade 368 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 1,899 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 8
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — Bavaria is not forgiven
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 18 approaches from Bavaria and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Britain rebuffs 5 courts (open borders agreement)

## Turn 10 — Early February 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney moves from Munich to Franconia (126 lost to march, 253 to enemy harassment)
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Croatia, Franconia, Munich, Swabia, Tyrol.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 actions unused) Turn 11 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Massena [interrupted]: Massena hears cannon fire! Abandoning orders — rushing to Hungary! Massena moves from Tyrol to Bohemia. Bohemia falls to France! (was Austria) The pr…
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 13217 · net +817 · threat 73 · provinces 29 (+1) · ceiling 18984 · army 117661 · vassals Holland 89 · Kingdom of Italy 86 · Switzerland 54
  - NET income 2638 · trade 587 · admin 50 · tribute 712 · upkeep 904 · charges 1588 · contributions 150 · occupation 70 · blockade 368 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 5 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France

## Turn 11 — Late February 1806
  - MAILBOX #9 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #10 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #11 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain + Russia (7 pairs resolved). Status quo: Bohemia stays ours by the treaty — titled. Status quo: Tyrol stays Bavarian by the treaty. Status quo: Milan stays Austrian by the treaty. → display-only
- CMD `Ney, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Lannes, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Swabia to Franconia (106 lost to march, 212 to enemy harassment)
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 1 action unused) Turn 12 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: drill×1, wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 15760 · net +2437 · threat 39 · provinces 29 (+0) · ceiling 73761 · army 117343 · vassals Holland 87 · Kingdom of Italy 79 · Switzerland 51
  - NET income 2639 · trade 587 · admin 50 · tribute 712 · upkeep 904 · charges 577 · occupation 70
- DISPATCH: Sire — the war with Britain is over. The peace grants safe passage home.
  - RAIL status_quo_conceded: Milan — left with Austria by the peace, titled to them by treaty.
  - RAIL settlement_summary: Settlement of France vs Austria + Britain + Russia: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 3
- COURTS: The court of Britain eases over The Low Countries — service to the strong is now the length of its tether.
- COURTS: The court of Austria eases over Revanche — alliance is now the length of its tether.
- COURTS: And Sardinia stirs at its own design.
- DIPLO +9 medium/low (diplomatic_coalition_dissolved, status_quo_titled, diplomatic_dp_regen, diplomatic_vassal_contingent ×2, blockade_broken ×3, agenda_shift)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 73 to 36.
  - LOG ai_ai_proposal_refused: Britain rebuffs Bavaria (open borders agreement)

## Turn 12 — Early March 1806
  - MAILBOX #10 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #12 → refuse the petition
  - POPUP proposal_result: Holland's petition for relief is refused: loyalty −10 (87 → 77); bond 0 → -20 (-1 a turn). Nothing is charged. → display-only
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Munich, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 18740 · net +2945 · threat 42 · provinces 29 (+0) · ceiling 264083 · army 117343 · vassals Holland 74 · Kingdom of Italy 77 · Switzerland 48
  - NET income 2740 · trade 587 · admin 50 · tribute 712 · upkeep 904 · charges 200 · occupation 40
- DISPATCH: Sire — Lannes has now gone unrewarded 6 turns. The staff have noticed which of us he no longer looks at.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 5
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 10 courts rebuff Austria (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 13 — Late March 1806
  - MAILBOX #11 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #13 → refuse the petition
  - POPUP proposal_result: The Kingdom of Italy's petition for relief is refused: loyalty −10 (77 → 67); bond 0 → -20 (-1 a turn). Nothing is charged. → display-only
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #14 → 1
  -     ↳ refused: The armistice with Austria holds for 3 more turns. We cannot declare war until it expires.
- CMD `Davout, move to Franconia` → ✗ Davout is already in Franconia.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 actions unused) Turn 14 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: drill×1, wait×1
- LEDGER treasury 21685 · net +2909 · threat 45 · provinces 29 (+0) · ceiling 264083 · army 117343 · vassals Holland 71 · Kingdom of Italy 64 · Switzerland 40
  - NET income 2740 · trade 587 · admin 50 · tribute 712 · upkeep 904 · charges 236 · occupation 40
- DISPATCH: Sire — London now pays Vienna 300 gold a turn against us. Her peace with us binds her 2 more turns.
  - TURN EVENTS 4
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)
  - LOG ai_ai_proposal_refused: 12 courts rebuff Bavaria (open borders agreement)

## Turn 14 — Early April 1806
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Fra…
- CMD `Massena, move to Tyrol` → ✗ Not enough actions! Need 1, have 0 — Massena cannot march to Tyrol today.
- CMD `end turn` → ✓ Turn 14 ended. Turn 15 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- LEDGER treasury 24594 · net +2874 · threat 45 · provinces 29 (+0) · ceiling 264083 · army 117343 · vassals Holland 68 · Kingdom of Italy 61 · Switzerland 32
  - NET income 2740 · trade 587 · admin 50 · tribute 712 · upkeep 904 · charges 271 · occupation 40
- DISPATCH: Sire — Lannes's claim is 8 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 5
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Bavaria (open borders agreement)

## Turn 15 — Late April 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: drill×1, wait×1
- LEDGER treasury 27538 · net +2909 · threat 45 · provinces 29 (+0) · ceiling 269916 · army 117343 · vassals Holland 65 · Kingdom of Italy 58 · Switzerland 24
  - NET income 2790 · trade 587 · admin 50 · tribute 712 · upkeep 904 · charges 306 · occupation 20
- DISPATCH: Sire — Austria, Britain and Russia would now join a league against us (relations −75, −85 and −75). The Balance of Europe names the price to keep each out.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_vassal_unrest)
  - LOG ai_ai_proposal_refused: Sardinia, Holland and Kingdom of Italy rebuff Bavaria (open borders agreement)

## Turn 16 — Early May 1806
- CMD `Ney, move to Bohemia` → ✓ Ney moves from Franconia to Bohemia
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Munich. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Not enough actions! Need 1, have 0 — Soult cannot march to Franconia today.
- CMD `end turn` → ✓ Turn 16 ended. Turn 17 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 30447 · net +2874 · threat 45 · provinces 29 (+0) · ceiling 269916 · army 117343 · vassals Holland 62 · Kingdom of Italy 55 · Switzerland 16
  - NET income 2790 · trade 587 · admin 50 · tribute 712 · upkeep 904 · charges 341 · occupation 20
- DISPATCH: Sire — relations between Austria and Russia have collapsed: Alliance → Defensive Alliance.
  - TURN EVENTS 4
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_vassal_unrest, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Bohemia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mo…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Munich. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Bohemia (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action unused) Turn 18 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, wait×1
- LEDGER treasury 33321 · net +2840 · threat 45 · provinces 29 (+0) · ceiling 269916 · army 117343 · vassals Holland 59 · Kingdom of Italy 52 · Switzerland 8
  - NET income 2790 · trade 587 · admin 50 · tribute 712 · upkeep 904 · charges 375 · occupation 20
- DISPATCH: Sire — Russia enacts the Divisional System — +1 order of the day, from the next refill; cures Slow to concentrate — the court's doctrine flaw — while its Staff stands.
  - RAIL diplomatic_vassal_rebellion_imminent: Sire — Switzerland is on the verge of rebellion!
  - TURN EVENTS 6
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_vassal_courting, diplomatic_dp_regen)

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP vassal_rebellion_imminent: Switzerland #15 → accept_vassal_rebellion
  - POPUP proposal_result: You accept the risk. If Switzerland's loyalty reaches zero, rebellion will follow. → display-only
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Franconia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1, wait×1
- LEDGER treasury 35119 · net +1629 · threat 38 · provinces 29 (+0) · ceiling 77520 · army 117343 · vassals Holland 46 · Kingdom of Italy 39
  - NET income 2790 · trade 587 · admin 50 · tribute 487 · upkeep 904 · charges 1271 · occupation 20 · admiralty 90
- DISPATCH: Sire — Switzerland is no longer ours. They have rebelled, and it is war.
  - RAIL diplomatic_alliance_cascade: Spain and Bavaria enter the war against Switzerland via their alliance with France.
  - RAIL diplomatic_vassal_rebellion: Sire — Switzerland has rebelled against France. It is war.
  - TURN EVENTS 5
- COURTS: The court of Britain hardens over The Low Countries — prepared now to go as far as an ultimatum.
- COURTS: The court of Austria hardens over Revanche — prepared now to go as far as an ultimatum.
- COURTS: And Sardinia stirs at its own design.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_relation_shift)
  - LOG defensive_cascade: Defensive cascade: Spain joins war via France
  - LOG defensive_cascade: Defensive cascade: Bavaria joins war via France
  - LOG vassal_auto_join_war: Vassal Holland joined France's war.
  - LOG vassal_auto_join_war: Vassal Kingdom of Italy joined France's war.
  - LOG vassal_broke_free: Vassal rebellion: Switzerland has broken free of France. War.

## Turn 19 — Late June 1806
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Bohemia. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✓ Lannes moves from Munich to Franconia (109 lost to march, 218 to enemy harassment)
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 2 actions unused) Turn 20 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, move×1, wait×1
- LEDGER treasury 36756 · net +1463 · threat 41 · provinces 29 (+0) · ceiling 71903 · army 115958 · vassals Holland 40 · Kingdom of Italy 33
  - NET income 2790 · trade 587 · admin 50 · tribute 487 · upkeep 896 · charges 1445 · occupation 20 · admiralty 90
- DISPATCH: Sire — 8 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 31 and declare on turn 34: Britain, Austria, Russia, Prussia and 4 lesser courts would march.
  - TURN EVENTS 3
- DIPLO +5 medium/low (law_enacted_abroad, diplomatic_vassal_courting, diplomatic_dp_regen, sovereign_takes_field, diplomatic_vassal_unrest)
  - LOG ai_ai_proposal_refused: 9 courts rebuff Austria (defensive alliance)

## Turn 20 — Early July 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 actions unused) Turn 21 begins!
- enemy phase: 6 actions, 2 attacks — Britain, Russia, Austria and 5 other courts stirred as well, but their formations remain beyond our sight. — Castanos assaults the Bern garrison! Garrison: 10,000 -> 5,391 (-4,609). Castanos loses 3,472 troops. Garrison holds — … · Castanos assaults the Bern garrison! Garrison collapses (5,391 -> 0). Castanos loses 2,079 troops in the assault. Casta…
  - 🏴 Spain: [Materiel] Guns, horses and stores lost with the fallen: Spain -103g, Switzerland -134g. Captured: Switzerland → Spain
  - verbs: attack×2, recruit×2, move×1, wait×1
- LEDGER treasury 39353 · net +2566 · threat 42 · provinces 29 (+0) · ceiling 253166 · army 114932 · vassals Holland 32 · Kingdom of Italy 25
  - NET income 2790 · trade 587 · admin 50 · tribute 487 · upkeep 880 · charges 448 · occupation 20
- DISPATCH: Sire — Switzerland is knocked out of the war. No army remains beneath their colours.
  - RAIL nation_eliminated: Sire — Switzerland has been eliminated from the war.
  - TURN EVENTS 5
- COURTS: The court of Britain eases over The Low Countries — service to the strong is now the length of its tether.
- COURTS: The court of Austria eases over Revanche — alliance is now the length of its tether.
- COURTS: And Sardinia stirs at its own design.
- DIPLO +5 medium/low (law_enacted_abroad, diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest ×2)

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 actions unused) Turn 22 begins!
- enemy phase: 5 actions, 0 attacks — Britain, Russia, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×3, fortify×1, wait×1
- LEDGER treasury 41919 · net +2535 · threat 43 · provinces 29 (+0) · ceiling 253166 · army 113937 · vassals Holland 24 · Kingdom of Italy 17
  - NET income 2790 · trade 587 · admin 50 · tribute 487 · upkeep 880 · charges 479 · occupation 20
- DISPATCH: Sire — Lannes's claim is 15 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_defection_cascade: The empire trembles — multiple vassals are wavering!
  - TURN EVENTS 7
- DIPLO +8 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_vassal_courting ×2, diplomatic_dp_regen, diplomatic_vassal_unrest ×2, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)
  - LOG nation_eliminated: Switzerland has been eliminated from the war.

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Bohemia. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 actions unused) Turn 23 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 44462 · net +2513 · threat 44 · provinces 29 (+0) · ceiling 253833 · army 112972 · vassals Holland 16 · Kingdom of Italy 9
  - NET income 2790 · trade 587 · admin 50 · tribute 487 · upkeep 872 · charges 509 · occupation 20
- DISPATCH: Sire — Lannes's claim is 16 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_vassal_rebellion_imminent: Sire — the Kingdom of Italy is on the verge of rebellion!
  - RAIL diplomatic_defection_cascade: The empire trembles — multiple vassals are wavering!
  - TURN EVENTS 4
- DIPLO +3 medium/low (diplomatic_vassal_courting, diplomatic_dp_regen, diplomatic_vassal_unrest)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
  - POPUP vassal_rebellion_imminent: KingdomOfItaly #17 → accept_vassal_rebellion
  - POPUP proposal_result: You accept the risk. If KingdomOfItaly's loyalty reaches zero, rebellion will follow. → display-only
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action unused) Turn 24 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 46983 · net +2491 · threat 45 · provinces 29 (+0) · ceiling 254500 · army 112036 · vassals Holland 8 · Kingdom of Italy 1
  - NET income 2790 · trade 587 · admin 50 · tribute 487 · upkeep 864 · charges 539 · occupation 20
- DISPATCH: Sire — 4 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 31 and declare on turn 34: Britain, Austria, Russia and 3 lesser courts would march.
  - RAIL diplomatic_vassal_rebellion_imminent: Sire — Holland is on the verge of rebellion!
  - RAIL diplomatic_vassal_rebellion_imminent: Sire — the Kingdom of Italy is on the verge of rebellion!
  - RAIL diplomatic_defection_cascade: The empire trembles — multiple vassals are wavering!
  - TURN EVENTS 4
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
  - POPUP vassal_rebellion_imminent: Holland #18 → accept_vassal_rebellion
  - POPUP proposal_result: You accept the risk. If Holland's loyalty reaches zero, rebellion will follow. → display-only
  - POPUP vassal_rebellion_imminent: KingdomOfItaly #19 → accept_vassal_rebellion
  - POPUP proposal_result: You accept the risk. If KingdomOfItaly's loyalty reaches zero, rebellion will follow. → display-only
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Bohemia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 actions unused) Turn 25 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 49003 · net +1995 · threat 26 · provinces 29 (+0) · ceiling 215250 · army 111128 · vassals none
  - NET income 2790 · trade 587 · admin 50 · upkeep 848 · charges 564 · occupation 20
- DISPATCH: Sire — Holland is no longer ours. They broke free and stand alone.
  - RAIL diplomatic_defection_cascade: The empire trembles — multiple vassals are wavering!
  - RAIL diplomatic_vassal_broke_free_peace: Sire — Holland breaks free of France and stands alone — an independent power, and no war declared.
  - RAIL diplomatic_vassal_broke_free_peace: Sire — the Kingdom of Italy breaks free of France and stands alone — an independent power, and no war declared.
  - RAIL allegiance_in_play: The allegiance of Sardinia is in play — every court with gold or standing now bids for the flip.
  - RAIL design_promoted: REVANCHE: Kingdom of Italy will not forgive Austria the loss of Milan. A new design hardens in their court.
  - TURN EVENTS 5
- COURTS: The court of Sardinia hardens over The House of Savoy Restored — prepared now to go as far as an ultimatum.
- DIPLO +8 medium/low (law_enacted_abroad, diplomatic_vassal_courting ×2, diplomatic_dp_regen, agenda_shift ×2, diplomatic_relation_shift ×2)
  - LOG vassal_broke_free: Vassal rebellion: Holland breaks free of France and stands alone.
  - LOG vassal_broke_free: Vassal rebellion: KingdomOfItaly breaks free of France and stands alone.
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)
  - LOG ai_ai_proposal_refused: Austria rebuffs Sardinia (defensive alliance)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 50998 · net +1972 · threat 27 · provinces 29 (+0) · ceiling 215250 · army 110246 · vassals none
  - NET income 2790 · trade 587 · admin 50 · upkeep 848 · charges 587 · occupation 20
- DISPATCH: Sire — Kingdom of Italy is no longer ours. They broke free and stand alone.
  - TURN EVENTS 5
- DIPLO +3 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen)
  - LOG design_promoted: REVANCHE: Kingdom of Italy swears to retake Milan — Austria is not forgiven

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 52970 · net +1948 · threat 28 · provinces 29 (+0) · ceiling 215250 · army 109391 · vassals none
  - NET income 2790 · trade 587 · admin 50 · upkeep 848 · charges 611 · occupation 20
- DISPATCH: Sire — Russia enacts the War Ministry under Arakcheev — +5 morale from every drill.
  - TURN EVENTS 5
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action unused) Turn 28 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 54934 · net +1940 · threat 32 · provinces 29 (+0) · ceiling 216583 · army 108563 · vassals none
  - NET income 2790 · trade 587 · admin 50 · upkeep 832 · charges 635 · occupation 20
- DISPATCH: Sire — Prussia enacts the Military Reorganisation Commission — +5 morale from every drill.
  - RAIL diplomatic_armed_peace_fuse: THE ARMED PEACE: 20 turns without a French battle — the courts re-arm. Europe's alarm rises 3 a turn toward the league gate at 60; Britain, Russia, A…
  - TURN EVENTS 4
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Bohemia. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 56882 · net +1925 · threat 36 · provinces 29 (+0) · ceiling 217250 · army 107760 · vassals none
  - NET income 2790 · trade 587 · admin 50 · upkeep 824 · charges 658 · occupation 20
- DISPATCH: Sire — Europe has watched us 21 quiet turns. At this pace the courts consult on turn 35 and declare on turn 38: Britain, Austria, Russia and 5 lesser courts would march. The cheapest court to keep ou…
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 58807 · net +1902 · threat 40 · provinces 29 (+0) · ceiling 217250 · army 106981 · vassals none
  - NET income 2790 · trade 587 · admin 50 · upkeep 824 · charges 681 · occupation 20
- DISPATCH: Sire — Europe has watched us 22 quiet turns. At this pace the courts consult on turn 35 and declare on turn 38: Britain, Austria, Russia and 5 lesser courts would march. The cheapest court to keep ou…
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Bohemia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 60717 · net +1887 · threat 44 · provinces 29 (+0) · ceiling 217916 · army 106225 · vassals none
  - NET income 2790 · trade 587 · admin 50 · upkeep 816 · charges 704 · occupation 20
- DISPATCH: Sire — Europe has watched us 23 quiet turns. At this pace the courts consult on turn 35 and declare on turn 38: Britain, Austria, Russia and 5 lesser courts would march. The cheapest court to keep ou…
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)

---
finished: **completed** · commands 150 · popups 40 · battles 20
