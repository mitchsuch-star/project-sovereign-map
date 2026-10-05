# Playtest digest — VOLTE

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
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
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, we do not court a belligerent — Austria is at war with us. The armistice and the settlement table are the war-time levers; intelligence and undermining are the mis…
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
  - POPUP diplomatic_dialogue: Switzerland, client_petition #9 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (82 → 92); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, we do not court a belligerent — Austria is at war with us. The armistice and the settlement table are the war-time levers; intelligence and undermining are the mis…
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
- LEDGER treasury 8317 · net +1422 · threat 79 · provinces 29 (+0) · ceiling 20319 · army 137798 · vassals Holland 93 · Kingdom of Italy 90 · Switzerland 92
  - NET income 2737 · trade 587 · admin 50 · tribute 487 · upkeep 1084 · charges 747 · contributions 110 · occupation 40 · blockade 368 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Gascony. No French corps stands in his path.
  - RAIL diplomatic_war_declared: Prussia has declared war on Hanover.
  - TURN EVENTS 10
- COURTS: The court of Prussia hardens over The Hanoverian Prize — prepared now to go as far as war.
- DIPLO +4 medium/low (enemy_marshal_commissioned, diplomatic_dp_regen, paymaster_subsidy, diplomatic_relation_shift)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG sponsorship_granted: Russia sponsors Britain against France (300g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 6 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 7 — Late December 1805
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, we do not court a belligerent — Austria is at war with us. The armistice and the settlement table are the war-time levers; intelligence and undermining are the mis…
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
- LEDGER treasury 9332 · net +1329 · threat 77 · provinces 29 (+0) · ceiling 19647 · army 125383 · vassals Holland 91 · Kingdom of Italy 88 · Switzerland 89
  - NET income 2725 · trade 587 · admin 50 · tribute 487 · upkeep 968 · charges 944 · contributions 110 · occupation 40 · blockade 368 · admiralty 90
- DISPATCH: Sire — Ney, crowned five turns ago, has been beaten in the field.
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 10
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia

## Turn 8 — Early January 1806
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, we do not court a belligerent — Austria is at war with us. The armistice and the settlement table are the war-time levers; intelligence and undermining are the mis…
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
- LEDGER treasury 10428 · net +1079 · threat 75 · provinces 28 (-1) · ceiling 18405 · army 119616 · vassals Holland 89 · Kingdom of Italy 86 · Switzerland 86
  - NET income 2590 · trade 587 · admin 50 · tribute 487 · upkeep 928 · charges 1139 · contributions 110 · blockade 368 · admiralty 90
- DISPATCH: Sire — Davout's corps has been broken at Bohemia. He must reform before he fights again.
  - RAIL design_promoted: REVANCHE: Hanover will not forgive Prussia the loss of Brunswick and 2 more provinces. A new design hardens in their court.
  - TURN EVENTS 8
- DIPLO +5 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG ai_ai_proposal_refused: 7 approaches from Austria, Prussia and Bavaria are rebuffed (open borders agreement)

## Turn 9 — Late January 1806
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, we do not court a belligerent — Austria is at war with us. The armistice and the settlement table are the war-time levers; intelligence and undermining are the mis…
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
- LEDGER treasury 11491 · net +889 · threat 73 · provinces 28 (+0) · ceiling 17910 · army 118214 · vassals Holland 89 · Kingdom of Italy 86 · Switzerland 85
  - NET income 2590 · trade 587 · admin 50 · tribute 487 · upkeep 904 · charges 1313 · contributions 150 · blockade 368 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 4 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL third_party_peace: THE CONGRESS: Hanover and Prussia have made their peace without France. Hanover pays 1,899 gold. Prussia is now free to look elsewhere.
  - TURN EVENTS 7
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG design_promoted: REVANCHE: Hanover swears to retake Brunswick and 2 more — Prussia is not forgiven
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — Bavaria is not forgiven
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 18 approaches from Bavaria and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Britain rebuffs 5 courts (open borders agreement)

## Turn 10 — Early February 1806
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, we do not court a belligerent — Austria is at war with us. The armistice and the settlement table are the war-time levers; intelligence and undermining are the mis…
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney moves from Munich to Franconia (126 lost to march, 253 to enemy harassment)
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Croatia, Franconia, Munich, Swabia, Tyrol.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 2 actions unused) Turn 11 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Massena [interrupted]: Massena hears cannon fire! Abandoning orders — rushing to Hungary! Massena moves from Tyrol to Bohemia. Bohemia falls to France! (was Austria) The pr…
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 12358 · net +714 · threat 73 · provinces 29 (+1) · ceiling 17395 · army 117661 · vassals Holland 89 · Kingdom of Italy 86 · Switzerland 84
  - NET income 2638 · trade 587 · admin 50 · tribute 487 · upkeep 904 · charges 1466 · contributions 150 · occupation 70 · blockade 368 · admiralty 90
- DISPATCH: Sire — the enemy has stood on our ground 5 turns. Every turn of it is worth a province to their recruiting sergeants.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria
  - LOG third_party_peace: THE CONGRESS: Hanover and Prussia make peace without France

## Turn 11 — Late February 1806
  - MAILBOX #9 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #10 → accept_settlement_offer
  - TERMS (settlement_confirm REVIEW): peace
  - POPUP diplomatic_dialogue: settlement_confirm #11 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain + Russia (7 pairs resolved). Status quo: Bohemia stays ours by the treaty — titled. Status quo: Tyrol stays Bavarian by the treaty. Status quo: Milan stays Austrian by the treaty. → display-only
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn.
  - POPUP diplomatic_dialogue: mission #12 → start_mission
- CMD `Ney, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Lannes, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Murat, move to Franconia` → ✓ Murat moves from Swabia to Franconia (106 lost to march, 212 to enemy harassment)
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 1 action unused) Turn 12 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: drill×1, wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 14712 · net +2256 · threat 39 · provinces 29 (+0) · ceiling 68404 · army 117343 · vassals Holland 87 · Kingdom of Italy 79 · Switzerland 83
  - NET income 2639 · trade 587 · admin 50 · tribute 487 · upkeep 904 · charges 533 · occupation 70
- MISSION Improving Relations — Austria · net +9 a turn · ≈23 turns to +100 at the present rate · beat running
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
- DIPLO +10 medium/low (diplomatic_coalition_dissolved, status_quo_titled, diplomatic_dp_regen, diplomatic_mission_progress, diplomatic_vassal_contingent ×2, blockade_broken ×3, agenda_shift)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 73 to 36.
  - LOG ai_ai_proposal_refused: Britain rebuffs Bavaria (open borders agreement)

## Turn 12 — Early March 1806
  - MAILBOX #10 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #13 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (87 → 97); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #14 → start_mission
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Munich, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 17143 · net +2402 · threat 42 · provinces 29 (+0) · ceiling 217250 · army 117343 · vassals Holland 96 · Kingdom of Italy 77 · Switzerland 82
  - NET income 2740 · trade 587 · admin 50 · tribute 150 · upkeep 904 · charges 181 · occupation 40
- MISSION Improving Relations — Austria · net +9 a turn · ≈22 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Lannes has now gone unrewarded 6 turns. The staff have noticed which of us he no longer looks at.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 5
- COURTS: The court of Russia hardens over The Gulf and the Straits — prepared now to go as far as service to the strong.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 13 — Late March 1806
  - MAILBOX #11 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #15 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (1200g forgone). Loyalty +10 (77 → 87); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #16 → start_mission
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #17 → 1
  -     ↳ refused: The armistice with Austria holds for 3 more turns. We cannot declare war until it expires.
- CMD `Davout, move to Franconia` → ✗ Davout is already in Franconia.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 actions unused) Turn 14 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: drill×1, wait×1
- LEDGER treasury 19395 · net +2450 · threat 45 · provinces 29 (+0) · ceiling 223500 · army 117343 · vassals Holland 95 · Kingdom of Italy 86 · Switzerland 81
  - NET income 2740 · trade 587 · admin 50 · tribute 225 · upkeep 904 · charges 208 · occupation 40
- MISSION Improving Relations — Austria · net +9 a turn · ≈21 turns to +100 at the present rate · beat running
- DISPATCH: Sire — London now pays Vienna 300 gold a turn against us. Her peace with us binds her 2 more turns.
  - TURN EVENTS 3
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG sponsorship_granted: Britain sponsors Austria against France (300g/turn)

## Turn 14 — Early April 1806
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #18 → start_mission
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Fra…
- CMD `Massena, move to Tyrol` → ✗ Not enough actions! Need 1, have 0 — Massena cannot march to Tyrol today.
- CMD `end turn` → ✓ Turn 14 ended. Turn 15 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 21845 · net +2420 · threat 45 · provinces 29 (+0) · ceiling 223500 · army 117343 · vassals Holland 94 · Kingdom of Italy 85 · Switzerland 80
  - NET income 2740 · trade 587 · admin 50 · tribute 225 · upkeep 904 · charges 238 · occupation 40
- MISSION Improving Relations — Austria · net +9 a turn · ≈20 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Lannes's claim is 8 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG ai_ai_proposal_refused: 12 courts rebuff Bavaria (open borders agreement)

## Turn 15 — Late April 1806
  - MAILBOX #12 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #19 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (80 → 90); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #20 → start_mission
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: drill×1, wait×1
- LEDGER treasury 24110 · net +2238 · threat 45 · provinces 29 (+0) · ceiling 210583 · army 117343 · vassals Holland 93 · Kingdom of Italy 84 · Switzerland 90
  - NET income 2790 · trade 587 · admin 50 · upkeep 904 · charges 265 · occupation 20
- MISSION Improving Relations — Austria · net +9 a turn · ≈19 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Austria, Britain and Russia would now join a league against us (relations −35, −85 and −75). The Balance of Europe names the price to keep each out.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)

## Turn 16 — Early May 1806
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #21 → start_mission
- CMD `Ney, move to Bohemia` → ✓ Ney moves from Franconia to Bohemia
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Munich. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Not enough actions! Need 1, have 0 — Soult cannot march to Franconia today.
- CMD `end turn` → ✓ Turn 16 ended. Turn 17 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 26348 · net +2211 · threat 45 · provinces 29 (+0) · ceiling 210583 · army 117343 · vassals Holland 92 · Kingdom of Italy 83 · Switzerland 90
  - NET income 2790 · trade 587 · admin 50 · upkeep 904 · charges 292 · occupation 20
- MISSION Improving Relations — Austria · net +9 a turn · ≈18 turns to +100 at the present rate · beat running
- DISPATCH: Sire — relations between Austria and Russia have collapsed: Alliance → Defensive Alliance.
  - TURN EVENTS 3
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG ai_ai_proposal_refused: 10 courts rebuff Bavaria (open borders agreement)

## Turn 17 — Late May 1806
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #22 → start_mission
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Bohemia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mo…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Munich. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Bohemia (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action unused) Turn 18 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: fortify×1, wait×1
- LEDGER treasury 28559 · net +2185 · threat 45 · provinces 29 (+0) · ceiling 210583 · army 117343 · vassals Holland 91 · Kingdom of Italy 82 · Switzerland 90
  - NET income 2790 · trade 587 · admin 50 · upkeep 904 · charges 318 · occupation 20
- MISSION Improving Relations — Austria · net +8 a turn · ≈17 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Russia enacts the Divisional System — +1 order of the day, from the next refill; cures Slow to concentrate — the court's doctrine flaw — while its Staff stands.
  - TURN EVENTS 5
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG ai_ai_proposal_refused: 9 courts rebuff Bavaria (open borders agreement)

## Turn 18 — Early June 1806
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #23 → start_mission
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Franconia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1, wait×1
- LEDGER treasury 30744 · net +2159 · threat 45 · provinces 29 (+0) · ceiling 210583 · army 117343 · vassals Holland 90 · Kingdom of Italy 81 · Switzerland 90
  - NET income 2790 · trade 587 · admin 50 · upkeep 904 · charges 344 · occupation 20
- MISSION Improving Relations — Austria · net +8 a turn · ≈16 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Europe has watched us 11 quiet turns. At this pace the courts consult on turn 30 and declare on turn 33: Britain, Russia, Prussia and 4 lesser courts would march. The cheapest court to keep ou…
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (defensive alliance)

## Turn 19 — Late June 1806
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #24 → start_mission
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Bohemia. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✓ Lannes moves from Munich to Franconia (109 lost to march, 218 to enemy harassment)
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 2 actions unused) Turn 20 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 32903 · net +2470 · threat 45 · provinces 29 (+0) · ceiling 238666 · army 117016 · vassals Holland 89 · Kingdom of Italy 80 · Switzerland 90
  - NET income 2790 · trade 587 · admin 50 · tribute 337 · upkeep 904 · charges 370 · occupation 20
- MISSION Improving Relations — Austria · net +8 a turn · ≈15 turns to +100 at the present rate · beat running
- DISPATCH: Sire — 8 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 31 and declare on turn 34: Britain, Russia, Prussia and 4 lesser courts would march.
  - TURN EVENTS 2
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress)

## Turn 20 — Early July 1806
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #25 → start_mission
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 actions unused) Turn 21 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 35373 · net +2590 · threat 45 · provinces 29 (+0) · ceiling 251166 · army 117016 · vassals Holland 88 · Kingdom of Italy 79 · Switzerland 90
  - NET income 2790 · trade 587 · admin 50 · tribute 487 · upkeep 904 · charges 400 · occupation 20
- MISSION Improving Relations — Austria · net +7 a turn · ≈14 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Russia enacts Arakcheev's Artillery — artillery levies cost 15% less (×0.85).
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 3
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress)

## Turn 21 — Late July 1806
  - MAILBOX #13 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #26 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +10 (88 → 98); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #27 → start_mission
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 actions unused) Turn 22 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1, wait×1
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 37626 · net +2226 · threat 45 · provinces 29 (+0) · ceiling 223083 · army 117016 · vassals Holland 98 · Kingdom of Italy 78 · Switzerland 90
  - NET income 2790 · trade 587 · admin 50 · tribute 150 · upkeep 904 · charges 427 · occupation 20
- MISSION Improving Relations — Austria · net +7 a turn · ≈13 turns to +100 at the present rate · beat running
- DISPATCH: Sire — relations between Austria and Russia have collapsed: Defensive Alliance → Non-Aggression.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +5 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_mission_progress, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (DEFENSIVE ALLIANCE → NON AGGRESSION)

## Turn 22 — Early August 1806
  - MAILBOX #14 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #28 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (1200g forgone). Loyalty +10 (78 → 88); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #29 → start_mission
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Bohemia. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 actions unused) Turn 23 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 39702 · net +2276 · threat 45 · provinces 29 (+0) · ceiling 229333 · army 117016 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2790 · trade 587 · admin 50 · tribute 225 · upkeep 904 · charges 452 · occupation 20
- MISSION Improving Relations — Austria · net +7 a turn · ≈12 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Europe has watched us 15 quiet turns. At this pace the courts consult on turn 31 and declare on turn 34: Britain, Russia and 3 lesser courts would march. The cheapest court to keep out of it i…
  - TURN EVENTS 2
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)

## Turn 23 — Late August 1806
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #30 → start_mission
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action unused) Turn 24 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 41978 · net +2249 · threat 45 · provinces 29 (+0) · ceiling 229333 · army 117016 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2790 · trade 587 · admin 50 · tribute 225 · upkeep 904 · charges 479 · occupation 20
- MISSION Improving Relations — Austria · net +7 a turn · ≈11 turns to +100 at the present rate · beat running
- DISPATCH: Sire — 4 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 31 and declare on turn 34: Britain, Russia and 3 lesser courts would march.
  - TURN EVENTS 2
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 24 — Early September 1806
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #31 → start_mission
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Bohemia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 actions unused) Turn 25 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 44227 · net +2222 · threat 45 · provinces 29 (+0) · ceiling 229333 · army 117016 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2790 · trade 587 · admin 50 · tribute 225 · upkeep 904 · charges 506 · occupation 20
- MISSION Improving Relations — Austria · net +7 a turn · ≈10 turns to +100 at the present rate · beat running
- DISPATCH: Sire — London now pays Vienna 500 gold a turn against us. The coalition has its paymaster; it lacks only its armies.
  - TURN EVENTS 2
- COURTS: The court of Austria eases over Revanche — gold is now the length of its tether.
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)

## Turn 25 — Late September 1806
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #32 → start_mission
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Austria open borders
- LEDGER treasury 46449 · net +2195 · threat 45 · provinces 29 (+0) · ceiling 229333 · army 117016 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2790 · trade 587 · admin 50 · tribute 225 · upkeep 904 · charges 533 · occupation 20
- MISSION Improving Relations — Austria · net +7 a turn · ≈9 turns to +100 at the present rate · beat running
- DISPATCH: Sire — 2 more quiet turns and the courts of Europe re-arm. At this pace the courts consult on turn 31 and declare on turn 34: Britain, Russia and 3 lesser courts would march.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +4 medium/low (law_enacted_abroad, doctrine_cured_abroad, diplomatic_dp_regen, diplomatic_mission_progress)

## Turn 26 — Early October 1806
  - MAILBOX #15 Austria incoming_proposal: Austria — Open Borders Agreement → activated
  - POPUP diplomatic_dialogue: Austria, open_borders #33 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: Peace → Open Borders with Austria. → display-only
- CMD `Talleyrand, improve relations with Austria` → ✓ Sire, I shall begin efforts to improve relations with Austria. This will cost 1 DP per turn. Note: this will replace my current mission to improve relations with Austria.
  - POPUP diplomatic_dialogue: mission #34 → start_mission
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Austria alliance
- LEDGER treasury 49256 · net +2006 · threat 41 · provinces 28 (-1) · ceiling 216416 · army 117016 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2590 · trade 612 · admin 50 · tribute 225 · upkeep 904 · charges 567
- MISSION Improving Relations — Austria · net +7 a turn · ≈8 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Sire — Austria and France have signed the Open Borders Agreement.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 4
- COURTS: The court of Austria hardens over Revanche — prepared now to go as far as an ultimatum.
- DIPLO +4 medium/low (diplomatic_treaty_signed, law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (design ask)

## Turn 27 — Late October 1806
  - MAILBOX #16 Austria incoming_proposal: Austria — Full Alliance → activated
  - POPUP diplomatic_dialogue: Austria, alliance #35 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: Open Borders → Alliance with Austria. → display-only
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, an ally is reassured, not courted — the Reassure mission is the maintenance of our alliance with Austria.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action unused) Turn 28 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1, wait×1
- LEDGER treasury 51299 · net +2019 · threat 38 · provinces 28 (+0) · ceiling 219500 · army 117016 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2590 · trade 649 · admin 50 · tribute 225 · upkeep 904 · charges 591
- MISSION Improving Relations — Austria · net +7 a turn · ≈7 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Sire — Austria and France have signed the Full Alliance.
  - RAIL volte_face: THE VOLTE-FACE: Austria, beaten and then courted, takes France's hand. Her court turns its gaze to The Eastern Question.
  - TURN EVENTS 3
- DIPLO +7 medium/low (balance_of_europe_shifted, diplomatic_treaty_signed, law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress, agenda_shift ×2)
  - LOG ai_ai_proposal_refused: 2 approaches from Russia and Austria are rebuffed (design ask)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Russia (defensive alliance)
  - LOG balance_of_europe_shifted: Austrian-led alignment leads the current largest alignment at 47% of active European bloc power.

## Turn 28 — Early November 1806
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, an ally is reassured, not courted — the Reassure mission is the maintenance of our alliance with Austria.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Bohemia. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 53318 · net +2332 · threat 35 · provinces 28 (+0) · ceiling 247583 · army 117016 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2590 · trade 649 · admin 50 · tribute 562 · upkeep 904 · charges 615
- MISSION Improving Relations — Austria · net +7 a turn · ≈6 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Austria moves toward war with Ottoman Empire. The design is open; the timing is not.
  - RAIL crisis_brewing: THE BREWING CRISIS: Austria will move on Ottoman. You may compensate (1,200g — you can afford it); guarantee Ottoman (1 DP — 6 in hand); or let the w…
  - TURN EVENTS 2
- COURTS: The court of Russia hardens over Arbiter of Europe — prepared now to go as far as an ultimatum.
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG design_bought_off: Ottoman Empire buys off Austria's design — the want sleeps
  - LOG volte_face: THE VOLTE-FACE: Austria, beaten and then courted, takes France's hand

## Turn 29 — Late November 1806
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, an ally is reassured, not courted — the Reassure mission is the maintenance of our alliance with Austria.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 55650 · net +2454 · threat 32 · provinces 28 (+0) · ceiling 260083 · army 117016 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2590 · trade 649 · admin 50 · tribute 712 · upkeep 904 · charges 643
- MISSION Improving Relations — Austria · net +7 a turn · ≈5 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Austria moves toward war with Ottoman Empire. The design is open; the timing is not.
  - RAIL crisis_passed: Austria stands down over Ottoman, Sire — the design was bought off — compensation stands.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)

## Turn 30 — Early December 1806
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, an ally is reassured, not courted — the Reassure mission is the maintenance of our alliance with Austria.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Bohemia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 58104 · net +2424 · threat 29 · provinces 28 (+0) · ceiling 260083 · army 117016 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2590 · trade 649 · admin 50 · tribute 712 · upkeep 904 · charges 673
- MISSION Improving Relations — Austria · net +7 a turn · ≈4 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Austria stands down over Ottoman Empire; the design was bought off, and the bargain stands.
  - TURN EVENTS 3
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_progress)

## Turn 31 — Late December 1806
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, an ally is reassured, not courted — the Reassure mission is the maintenance of our alliance with Austria.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Bohemia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mo…
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action unused) Turn 32 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 60528 · net +2395 · threat 26 · provinces 28 (+0) · ceiling 260083 · army 117016 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2590 · trade 649 · admin 50 · tribute 712 · upkeep 904 · charges 702
- MISSION Improving Relations — Austria · net +7 a turn · ≈3 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Britain, Russia and 3 lesser courts would join a league, but at this pace none gathers within 40 turns. The cheapest court to keep out of it is Hanover: Talleyrand brings her to −10 in 1 turn …
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)

## Turn 32 — Early January 1807
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, an ally is reassured, not courted — the Reassure mission is the maintenance of our alliance with Austria.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Bohemia. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 actions unused) Turn 33 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 62923 · net +2366 · threat 23 · provinces 28 (+0) · ceiling 260083 · army 117016 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2590 · trade 649 · admin 50 · tribute 712 · upkeep 904 · charges 731
- MISSION Improving Relations — Austria · net +7 a turn · ≈2 turns to +100 at the present rate · beat running
- DISPATCH: Sire — Britain, Russia and 3 lesser courts would join a league, but at this pace none gathers within 40 turns. The cheapest court to keep out of it is Hanover: Talleyrand brings her to −10 in 1 turn …
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)

## Turn 33 — Late January 1807
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, an ally is reassured, not courted — the Reassure mission is the maintenance of our alliance with Austria.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 1 action unused) Turn 34 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 65289 · net +2338 · threat 20 · provinces 28 (+0) · ceiling 260083 · army 117016 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2590 · trade 649 · admin 50 · tribute 712 · upkeep 904 · charges 759
- MISSION Improving Relations — Austria · net +1 a turn · ≈1 turn to +100 at the present rate · beat running
- DISPATCH: Sire — Britain, Russia and 3 lesser courts would join a league, but at this pace none gathers within 40 turns. The cheapest court to keep out of it is Hanover: Talleyrand brings her to −10 in 1 turn …
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_mission_progress)
  - LOG ai_ai_proposal_refused: Austria rebuffs Russia (design ask)

## Turn 34 — Early February 1807
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, an ally is reassured, not courted — the Reassure mission is the maintenance of our alliance with Austria.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Bohemia. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 actions unused) Turn 35 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 67602 · net +2285 · threat 17 · provinces 28 (+0) · ceiling 258000 · army 117016 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2590 · trade 624 · admin 50 · tribute 712 · upkeep 904 · charges 787
- MISSION ended: Improving Relations — Austria, relations reached +100
- DISPATCH: Sire — relations between France and Spain have collapsed: Alliance → Defensive Alliance.
  - TURN EVENTS 3
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_mission_completed, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 35 — Late February 1807
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, an ally is reassured, not courted — the Reassure mission is the maintenance of our alliance with Austria.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action unused) Turn 36 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 69887 · net +2258 · threat 14 · provinces 28 (+0) · ceiling 258000 · army 117016 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2590 · trade 624 · admin 50 · tribute 712 · upkeep 904 · charges 814
- DISPATCH: Sire — Britain, Russia and 3 lesser courts would join a league, but at this pace none gathers within 40 turns. The cheapest court to keep out of it is Hanover: Talleyrand brings her to −10 in 1 turn …
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 36 — Early March 1807
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, an ally is reassured, not courted — the Reassure mission is the maintenance of our alliance with Austria.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Bohemia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mo…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Bohemia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 2 actions unused) Turn 37 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 72145 · net +2231 · threat 11 · provinces 28 (+0) · ceiling 258000 · army 117016 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2590 · trade 624 · admin 50 · tribute 712 · upkeep 904 · charges 841
- DISPATCH: Sire — Lannes's claim is 30 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 37 — Late March 1807
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, an ally is reassured, not courted — the Reassure mission is the maintenance of our alliance with Austria.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 2 actions unused) Turn 38 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 74376 · net +2204 · threat 8 · provinces 28 (+0) · ceiling 258000 · army 117016 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2590 · trade 624 · admin 50 · tribute 712 · upkeep 904 · charges 868
- DISPATCH: Sire — Lannes's claim is 31 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 38 — Early April 1807
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, an ally is reassured, not courted — the Reassure mission is the maintenance of our alliance with Austria.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Bohemia. Army is now mobile.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 3 actions unused) Turn 39 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 76580 · net +2178 · threat 5 · provinces 28 (+0) · ceiling 258000 · army 117016 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2590 · trade 624 · admin 50 · tribute 712 · upkeep 904 · charges 894
- DISPATCH: Sire — Lannes's claim is 32 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 39 — Late April 1807
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, an ally is reassured, not courted — the Reassure mission is the maintenance of our alliance with Austria.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 2 actions unused) Turn 40 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 78758 · net +2151 · threat 2 · provinces 28 (+0) · ceiling 258000 · army 117016 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2590 · trade 624 · admin 50 · tribute 712 · upkeep 904 · charges 921
- DISPATCH: Sire — Lannes's claim is 33 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria rebuffs Russia (design ask)

## Turn 40 — Early May 1807
- CMD `Talleyrand, improve relations with Austria` → ✗ Sire, an ally is reassured, not courted — the Reassure mission is the maintenance of our alliance with Austria.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Bohemia (+2% defense).
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 actions unused) Turn 41 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 80909 · net +2126 · threat 0 · provinces 28 (+0) · ceiling 258000 · army 117016 · vassals Holland 98 · Kingdom of Italy 88 · Switzerland 90
  - NET income 2590 · trade 624 · admin 50 · tribute 712 · upkeep 904 · charges 946
- DISPATCH: Sire — Britain, Russia and 2 lesser courts would join a league, but at this pace none gathers within 40 turns. The cheapest court to keep out of it is Sweden: Talleyrand brings her to −10 in 2 turns …
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

---
finished: **completed** · commands 236 · popups 58 · battles 20
