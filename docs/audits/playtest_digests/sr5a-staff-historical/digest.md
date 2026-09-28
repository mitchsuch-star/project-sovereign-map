# Playtest digest — sr5a-staff-historical

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `716b09a7294c` (dirty) · content `dcf75e5f3732` · driver `aef52ad7cbfd`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 800.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (24,000; expect about 78,676 with the corps likely to arrive, up to 96,789 if all march) vs Mack (large force) at Swabia — the balance of force looks favora…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 1850, own corps) vs Mack (lost 15045) — Reinforcements from Davout, Lannes and Napoleon bolstered Ney's position — though Soult, Murat and Bernadotte never arr…
- CMD `Davout, move to Swabia` → ✗ Davout is already in Swabia.
- CMD `Lannes, move to Rhineland` → ✓ Lannes moves from Swabia to Rhineland
- CMD `end turn` → ✓ Turn 1 ended. (Warning: 2 actions unused) Turn 2 begins!
- enemy phase: 2 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles's forces press forward aggressively. Brutal stalemate between ArchdukeCharles and Massena. Heavy casual…
  - ⚔ Archduke Charles (lost 4271) vs Massena (lost 6140) — Stalemate. Massena and Archduke Charles glare at each other across the field.
  - verbs: attack×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Murat seeks an audience → acknowledge
  -     ↳ Murat's grievance runs its course.
  - POPUP diplomatic_dialogue: Prussia, open_borders #1 → accept
  - POPUP proposal_result: You have accepted Prussia's proposal. Treaty signed: Peace → Open Borders with Prussia. → display-only
- ENVOYS WAITING 3 · Prussia open borders · Ottoman open borders · Portugal open borders
- LEDGER treasury 1575 · net +1401 · threat 76 · provinces 28 · ceiling 33272 · army 175430 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 99
  - NET income 2590 · trade 400 · admin 50 · tribute 895 · upkeep 2194 · blockade 250 · admiralty 90
- DISPATCH: Supply cost you 1,099 men, at Swabia.
  - RAIL diplomatic_ai_proposal: An envoy from Prussia has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Ottoman Empire has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Portugal has arrived with a proposal.
  - TURN EVENTS 5
- DIPLO +6 medium/low (law_enacted_abroad, diplomatic_dp_regen, sovereign_takes_field, blockade_begins ×3)
  - LOG ai_ai_proposal_refused: Britain rebuffs Prussia and Bavaria (open borders agreement)

## Turn 2 — Early October 1805
  - LETTER Ottoman: Open Borders Agreement → accept
  - LETTER Portugal: Open Borders Agreement → accept
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 1,635.
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (21,398; expect about 88,830 with the corps likely to arrive, up to 98,694 if all march) vs Mack (substantial force) at Munich — the balance of force looks …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 696, own corps) vs Mack (lost 20031) — Davout and Massena arrived to reinforce Ney, but Napoleon failed to reach the field in time.
- CMD `Davout, attack Mack` → ✓ MUSTER — Davout (22,750; expect about 33,095 with the corps likely to arrive, up to 44,734 if all march) vs Mack (large force) at Tyrol — the balance of force looks even…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Davout (lost 8138) vs Archduke Charles (lost 1191, own corps) — Davout stood alone, Sire. Ney never came.
- CMD `Soult, move to Alsace` → ✗ Region 'Alsace' not found. From Lorraine the roads lead to: Swabia, Rhineland, Franche-Comte, Orleanais.
- CMD `Murat, move to Franche-Comte` → ✗ Murat is already in Franche-Comte.
- CMD `end turn` → ✓ Turn 2 ended. (Warning: 2 actions unused) Turn 3 begins!
- enemy phase: 7 actions, 2 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles strikes back after successfully defending! · ArchdukeCharles holds them at Franconia while allies attack from Tyrol! (+1 coordination)
  - ⚔ Archduke Charles (lost 1768) vs Bernadotte (lost 5474) — Bernadotte stood alone, Sire. Ney never came.
  - ⚔ Archduke Charles (lost 2612) vs Deroy (lost 5834) — Deroy was close. A period of drilling could have changed the outcome.
  - verbs: attack×2, wait×2, fortify×1, retreat×1, stance_change×1
- ENVOYS WAITING 2 · Denmark non aggression · Saxony open borders
- LEDGER treasury 2821 · net +1946 · threat 82 · provinces 28 (+0) · ceiling 34402 · army 156882 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 94
  - NET income 2590 · trade 450 · admin 50 · tribute 901 · upkeep 1624 · charges 50 · blockade 281 · admiralty 90
- DISPATCH: Sire — Davout's corps has been broken at Munich. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Denmark has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from Saxony has arrived with a proposal.
  - TURN EVENTS 6
- DIPLO +8 medium/low (diplomatic_treaty_signed ×3, diplomatic_we_threshold ×2, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Britain sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: 26 approaches from Prussia, Bavaria and Austria are rebuffed (open borders agreement)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 3 — Late October 1805
  - LETTER Denmark: Non-Aggression Pact → accept
  - LETTER Saxony: Open Borders Agreement → accept
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 2,903.
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (19,554; expect about 50,708 with the corps likely to arrive, up to 51,946 if all march) vs Mack (14,689 men) at Tyrol — the balance of force looks favorabl…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 631, own corps) vs Mack (lost 5976, own corps) — Massena's timely arrival bolstered Ney's position. Well-coordinated, Sire.
  - POPUP capture_choice[capture]: Tyrol, Ney → secure
- CMD `Davout, attack Mack` → ✗ Davout is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Rhineland to Swabia (166 lost to march)
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 700 gold (×3 at war) (×1.17 over the ordinance). Morale: 100% -> 94%
- CMD `end turn` → ✓ Turn 3 ended. (Warning: 2 actions unused) Turn 4 begins!
- SPENT 700g on this turn's orders
- enemy phase: 5 actions, 4 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles launches a decisive assault. ArchdukeCharles gains the advantage over Bernadotte. Casualties: ArchdukeC… · ArchdukeCharles attacks with overwhelming force. ArchdukeCharles gains the advantage over Deroy. Casualties: ArchdukeCh… · ArchdukeCharles assaults the Milan garrison! Garrison: 10,000 -> 5,000 (-5,000). ArchdukeCharles loses 2,976 troops. Ga… · ArchdukeCharles assaults the Milan garrison! Garrison collapses (5,000 -> 0). ArchdukeCharles loses 1,785 troops in the…
  - 🏴 Austria: [!] Bernadotte's troops are BROKEN (morale 0%)! FORCED RETREAT! Franconia has been captured by Austria!
  - 🏴 Austria: FORCED RETREAT! ArchdukeCharles advances into Munich. (2,328 lost to march) Munich has been captured by Austria!
  - 🏴 Austria: [Materiel] Guns, horses and stores lost with the fallen: Austria -89g, Kingdom of Italy -125g. Captured: KingdomOfItaly → Austria
  - ⚔ Archduke Charles (lost 752) vs Bernadotte (lost 7852) — Where were Ney and Lannes? Bernadotte held the field alone — reinforcement never came.
  - ⚔ Archduke Charles (lost 1149) vs Deroy (lost 5722) — Deroy held superior ground, yet Archduke Charles prevailed. A grim day, Sire.
  - verbs: attack×4, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Soult seeks an audience → acknowledge
  -     ↳ Soult's grievance runs its course.
- ENVOYS WAITING 2 · Hesse non aggression · PapalStates open borders
- LEDGER treasury 3800 · net +1914 · threat 90 · provinces 29 (+1) · ceiling 22418 · army 147464 · vassals Holland 96 · Kingdom of Italy 96 · Switzerland 91
  - NET income 2617 · trade 525 · admin 50 · tribute 712 · upkeep 1334 · charges 185 · occupation 52 · blockade 329 · admiralty 90
- DISPATCH: Sire — Bernadotte's corps has been broken at Franconia. He must reform before he fights again.
  - RAIL diplomatic_ai_proposal: An envoy from Hesse has arrived with a proposal.
  - RAIL diplomatic_ai_proposal: An envoy from the Papal States has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Bavaria will not forgive Austria the loss of Franconia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 9
- DIPLO +5 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, diplomatic_dp_regen, agenda_shift)
  - LOG ai_ai_proposal_refused: 28 approaches rebuffed, chiefly from Bavaria and Prussia (open borders agreement)
  - LOG ai_ai_proposal_refused: 3 approaches from Prussia, Bavaria and Spain are rebuffed (open borders agreement)

## Turn 4 — Early November 1805
  - LETTER Hesse: Non-Aggression Pact → accept
  - LETTER PapalStates: Open Borders Agreement → accept
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 3,905.
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (17,946) vs Mack (small force) at Bohemia — the balance of force looks favorable.
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 81, own corps) vs Mack (lost 7286) — Reinforcements! Massena marched onto the field beside Ney. The enemy's advantage melted away.
- CMD `Davout, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Davout fortifies position at Franche-Comte. Defense bonus: +7% (grows +3% per t…
- CMD `Massena, move to Tyrol` → ✓ Massena moves from Bohemia to Tyrol (1,875 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 4 ended. Turn 5 begins!
- enemy phase: 5 actions, 1 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight. — ArchdukeCharles engages in solid combat. ArchdukeCharles gains the advantage over Bernadotte. Casualties: ArchdukeCharl…
  - 🏴 Austria: [!] MARSHAL CAPTURED — Bernadotte is taken by Austria at Tyrol!
  - ⚔ Archduke Charles (lost 2049) vs Bernadotte (lost 396, own corps) — Ney never reached the guns. The battle was decided without them, Sire. And Bernadotte was taken on that field — Austria…
  - verbs: attack×1, retreat×1, stance_change×1, move×1, wait×1
- LEDGER treasury 5923 · net +1967 · threat 91 · provinces 29 (+0) · ceiling 23932 · army 138356 · vassals Holland 95 · Kingdom of Italy 95 · Switzerland 88
  - NET income 2614 · trade 587 · admin 50 · tribute 712 · upkeep 1108 · charges 428 · requisitions 50 · occupation 52 · blockade 368 · admiralty 90
- DISPATCH: Sire — Marshal Bernadotte has been taken. Austria holds him prisoner.
  - TURN EVENTS 4
- DIPLO +6 medium/low (diplomatic_treaty_signed ×2, diplomatic_we_threshold, law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples and Denmark rebuff Bavaria (open borders agreement)
  - LOG design_promoted: REVANCHE: Bavaria swears to retake Franconia and 1 more — Austria is not forgiven

## Turn 5 — Late November 1805
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 5,923.
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (17,687; expect about 45,047 with the corps likely to arrive, up to 49,368 if all march) vs Archduke Charles (26,616 men) at Franconia — the balance of forc…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 666, own corps) vs Archduke Charles (lost 4893) — Lannes, Massena and Napoleon's timely arrival bolstered Ney's position. Well-coordinated, Sire.
- CMD `Lannes, attack Mack` → ✗ Lannes is engaged with Archduke Charles and cannot begin a strategic march. Deal with the engagement first.
- CMD `Soult, move to Swabia` → ✓ Soult moves from Lorraine to Swabia (990 lost to march)
- CMD `Murat, move to Swabia` → ✓ Murat moves from Franche-Comte to Swabia (308 lost to march)
- CMD `end turn` → ✓ Turn 5 ended. (Warning: 1 action unused) Turn 6 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: retreat×1, stance_change×1, wait×1
  - POPUP marshal_audience: jealousy_confrontation, Marshal Massena seeks an audience → acknowledge
  -     ↳ Massena's grievance runs its course.
  - POPUP diplomatic_dialogue: Switzerland, client_petition #9 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +10 (87 → 97); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 7846 · net +1581 · threat 92 · provinces 29 (+0) · ceiling 21710 · army 131675 · vassals Holland 96 · Kingdom of Italy 96 · Switzerland 97
  - NET income 2615 · trade 587 · admin 50 · tribute 487 · upkeep 1032 · charges 666 · requisitions 50 · occupation 52 · blockade 368 · admiralty 90
- DISPATCH: Supply cost you 2,621 men, at Franconia.
  - RAIL expedition_landed: THE LANDING: Paget has put 5,000 men ashore at Lisbon.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Austria

## Turn 6 — Early December 1805
- CMD `enact the Staff` → ✗ The Grand Quartier Général costs 9,000 gold; the treasury holds 7,846.
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Archduke Charles is at Bohemia, just one region away.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archd…
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke Charles at Bohemia instead.) → trust
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 619, own corps) vs Archduke Charles (lost 5529) — Reinforcements! Ney, Massena and Napoleon marched onto the field beside Lannes. The enemy's advantage melted away.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 3 actions unused) Turn 7 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 9353 · net +1426 · threat 93 · provinces 29 (+0) · ceiling 21391 · army 126614 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 97
  - NET income 2616 · trade 587 · admin 50 · tribute 487 · upkeep 984 · charges 870 · requisitions 50 · occupation 52 · blockade 368 · admiralty 90
- DISPATCH: Sire — Leon has been taken by Britain.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 7 — Late December 1805
- CMD `enact the Staff` → ✓ The Grand Quartier Général (Berthier's Imperial Headquarters, expanded 1805–07): Berthier's headquarters grown into a true general staff: one more order carried each day…
  - POPUP clarification: The Council of State, The Grand Quartier Général (Berthier's Imperial Headquarters, expanded 1805–07): Berthier's headquarters grown into a true general staff: one more order carried each day. 9,000 gold now, then 300 gold a turn; one more order each day from the next refill. The treasury holds 9,353 gold. Enact it? (yes / no) → 1 (first option: Enact the Grand Quartier Général)
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (14,925; expect about 36,430 with the corps likely to arrive, up to 39,825 if all march) vs Archduke Charles (substantial force) at Vienna — the balance of …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 642, own corps) vs Archduke Charles (lost 4379, own corps) — Reinforcements! Lannes, Massena and Napoleon marched onto the field beside Ney. The enemy's advantage melted away.
- CMD `Davout, move to Bohemia` → ✓ Davout begins marching to Bohemia (distance: 3). Moved to Swabia. Route: Swabia -> Franconia -> Bohemia.
- CMD `Murat, attack Archduke Charles` → ✗ Not enough actions for a strategic pursuit! Need 2, have 1.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 1 action unused) Turn 8 begins!
- SPENT 9000g on this turn's orders
- enemy phase: 6 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, retreat×1, stance_change×1, move×1, wait×1
- ORDER Davout [active]: Davout is marching to Bohemia (3 turns remaining).
  - POPUP marshal_petition: jealousy_confrontation, Marshal Massena demands to be heard → acknowledge
  -     ↳ Massena's grievance runs its course.
- LEDGER treasury 2289 · net +2051 · threat 94 · provinces 29 (+0) · ceiling 18931 · army 119656 · vassals Holland 98 · Kingdom of Italy 98 · Switzerland 97
  - NET income 2617 · trade 587 · admin 50 · tribute 487 · upkeep 920 · charges 35 · requisitions 75 · occupation 52 · blockade 368 · admiralty 90 · laws 300
- DISPATCH: Supply cost you 4,160 men, at Vienna and Swabia.
  - TURN EVENTS 7
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Britain and Prussia rebuff Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (non-aggression pact)

## Turn 8 — Early January 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `Davout, attack Archduke Charles` → ✗ No intelligence on Archduke Charles's position, Sire. Scout for him before Davout can give chase.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Vie…
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shift…
- CMD `Massena, move to Milan` → ✓ Massena: 'ArchdukeCharles bars the way!' Engaging!
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Massena (lost 1068, own corps) vs Archduke Charles (lost 4802) — Reinforcements! Lannes and Napoleon marched onto the field beside Massena. The enemy's advantage melted away.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 1 action unused) Turn 9 begins!
- enemy phase: 9 actions, 4 attacks — Russia, Austria, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Castanos delivers an effective strike. Castanos gains the advantage over Paget. Casualties: Castanos 664, Paget 1,639. … · Deroy assaults the Munich garrison! Garrison: 10,000 -> 6,935 (-3,065). Deroy loses 3,472 troops. Garrison holds — 6,93… · Deroy assaults the Munich garrison! Garrison collapses (6,935 -> 0). Deroy loses 2,675 troops in the assault. Deroy mar… · Deroy marches from Munich into Franconia unopposed! (58 lost to march) Captured: Austria → Bavaria
  - 🏴 Bavaria: [Materiel] Guns, horses and stores lost with the fallen: Bavaria -133g, Austria -98g. Captured: Austria → Bavaria
  - 🏴 Bavaria: Deroy marches from Munich into Franconia unopposed! (58 lost to march) Captured: Austria → Bavaria
  - ⚔ Castanos (lost 664) vs Paget (lost 1639) — An aggressive stance invites disaster when one is not the attacker, Sire. Paget paid the price.
  - verbs: move×4, attack×4, unfortify×1
- ORDER Massena [active]: Massena is marching to Milan (4 turns remaining).
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 4259 · net +1809 · threat 95 · provinces 29 (+0) · ceiling 18477 · army 115212 · vassals Holland 99 · Kingdom of Italy 99 · Switzerland 97
  - NET income 2661 · trade 587 · admin 50 · tribute 487 · upkeep 888 · charges 287 · contributions 138 · requisitions 125 · occupation 30 · blockade 368 · admiralty 90 · laws 300
- DISPATCH: Sire — Paget has crossed into Berry. No French corps stands in his path.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: 12 courts rebuff Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: Bavaria rebuffs Austria (non-aggression pact)
  - LOG sponsorship_granted: Russia sponsors Britain against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sardinia against France (200g/turn)
  - LOG sponsorship_granted: Britain sponsors Sweden against France (200g/turn)
  - LOG ai_ai_proposal_refused: 19 approaches rebuffed, chiefly from Bavaria (open borders agreement)
  - LOG sponsorship_granted: Britain sponsors Russia against France (200g/turn)
  - LOG ai_ai_proposal_refused: 7 approaches to Britain and Russia are rebuffed (open borders agreement)

## Turn 9 — Late January 1806
  - MAILBOX #9 Austria incoming_proposal: Austria — Armistice → activated
  - POPUP diplomatic_dialogue: Austria, armistice_losing #11 → accept
  - POPUP proposal_result: You have accepted Austria's proposal. Treaty signed: At War → Armistice with Austria. → display-only
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Vienna. Army is now mobile.
- CMD `Lannes, move to Bohemia` → ✗ Lannes is already in Bohemia.
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 11.
- CMD `recruit 10000 cavalry with Murat` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 3 actions unused) Turn 10 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Massena [completed]: Massena arrives at Tyrol. Massena: "It is done. Point me at something that shoots back, Sire."
- ORDER Napoleon [completed]: Napoleon arrives at Tyrol.
- ORDER Ney [continues]: Ney marches to Bohemia. 1 region to Tyrol.
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 6054 · net +1554 · threat 93 · provinces 29 (+0) · ceiling 17966 · army 113212 · vassals Holland 99 · Kingdom of Italy 97 · Switzerland 96
  - NET income 2666 · trade 587 · admin 50 · tribute 487 · upkeep 880 · charges 528 · contributions 40 · occupation 30 · blockade 368 · admiralty 90 · laws 300
- DISPATCH: Sire — Paget has crossed into Normandy. No French corps stands in his path.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 6
- COURTS: The court of Austria eases over Redeem Italy — an ultimatum is now the length of its tether.
- DIPLO +5 medium/low (diplomatic_treaty_signed, law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 9 courts rebuff Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: 16 approaches from Bavaria and Austria are rebuffed (open borders agreement)

## Turn 10 — Early February 1806
  - MAILBOX #10 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #12 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (1200g forgone). Loyalty +3 (97 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney moves from Bohemia to Franconia (135 lost to march)
- CMD `Davout, fortify` → ✓ Davout fortifies position at Swabia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Franconia, Munich, Swabia.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 3 actions unused) Turn 11 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - 🏴 Bavaria: Deroy moves from Franconia to Bohemia. Bohemia falls to Bavaria!
  - verbs: move×2, unfortify×1, wait×1
- ENVOYS WAITING 1 · Britain settlement offer
- LEDGER treasury 7479 · net +1222 · threat 91 · provinces 29 (+0) · ceiling 16618 · army 111771 · vassals Holland 99 · Kingdom of Italy 99 · Switzerland 95
  - NET income 2671 · trade 587 · admin 50 · tribute 337 · upkeep 864 · charges 731 · contributions 40 · occupation 30 · blockade 368 · admiralty 90 · laws 300
- DISPATCH: Sire — 3 turns of famine at Swabia now. 4,071 men gone, and not one of them to the enemy. Bavaria's magazines feed us as our own — the army is simply too large for the province. Rhineland can feed 60…
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL design_promoted: REVANCHE: Austria will not forgive Bavaria the loss of Bohemia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 3
- DIPLO +3 medium/low (diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
  - LOG british_subsidy: Britain's gold: 300g reaches Russia
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 11 — Late February 1806
  - MAILBOX #11 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #13 → accept_settlement_offer
  - POPUP diplomatic_dialogue: settlement_confirm #14 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain + Russia (7 pairs resolved). Status quo: Tyrol stays ours by the treaty — titled. Status quo: Bohemia stays Bavarian by the treaty. Status quo: Milan stays Austrian by the treaty. → display-only
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `Ney, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Lannes, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #15 → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation #16 → reconsider
- CMD `Murat, move to Franconia` → ✓ Murat moves from Swabia to Franconia (196 lost to march)
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. (Warning: 1 action unused) Turn 12 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: drill×1, wait×1
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Ney: They settle into cold war.
  - POPUP diplomatic_dialogue: Holland, client_petition #17 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +3 (97 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 9912 · net +2067 · threat 45 · provinces 29 (+0) · ceiling 182083 · army 116575 · vassals Holland 100 · Kingdom of Italy 98 · Switzerland 94
  - NET income 2707 · trade 623 · admin 50 · upkeep 904 · charges 94 · occupation 15 · laws 300
- DISPATCH: Sire — the war with Britain is over. The peace grants safe passage home.
  - RAIL settlement_summary: Settlement of France + Spain + Holland + Bavaria + Kingdom of Italy vs Britain + Austria + Russia: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 6
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: And 3 other courts stir at their own designs.
- DIPLO +7 medium/low (diplomatic_coalition_dissolved, status_quo_titled, law_enacted_abroad, diplomatic_dp_regen, blockade_broken ×3)
  - LOG ai_ai_proposal_refused: 7 approaches from Britain and Russia are rebuffed (defensive alliance)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses
  - LOG design_promoted: REVANCHE: Austria swears to retake Bohemia and 1 more — Bavaria is not forgiven
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 91 to 45.
  - LOG ai_ai_proposal_refused: 8 courts rebuff Bavaria (open borders agreement)

## Turn 12 — Early March 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Bohemia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 2 actions unused) Turn 13 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
  - POPUP marshal_petition: jealousy_confrontation, Marshal Massena demands to be heard → acknowledge
  -     ↳ Massena's grievance runs its course.
- LEDGER treasury 11985 · net +2048 · threat 45 · provinces 29 (+0) · ceiling 182583 · army 116575 · vassals Holland 99 · Kingdom of Italy 97 · Switzerland 93
  - NET income 2713 · trade 623 · admin 50 · upkeep 904 · charges 119 · occupation 15 · laws 300
- DISPATCH: Sire — Marshal Lannes has now gone unrewarded 6 turns. The staff have noticed which of us he no longer looks at.
  - TURN EVENTS 8
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_ai_proposal_refused: Prussia rebuffs Britain and Russia (defensive alliance)
  - LOG ai_ai_proposal_refused: Sardinia, Holland and Kingdom of Italy rebuff Bavaria (open borders agreement)

## Turn 13 — Late March 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #18 → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation #19 → reconsider
- CMD `Davout, move to Franconia` → ✓ Davout moves from Swabia to Franconia (130 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 3 actions unused) Turn 14 begins!
- enemy phase: 4 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, drill×1, wait×1
- LEDGER treasury 14044 · net +2259 · threat 45 · provinces 29 (+0) · ceiling 202250 · army 115530 · vassals Holland 98 · Kingdom of Italy 96 · Switzerland 92
  - NET income 2716 · trade 623 · admin 50 · tribute 225 · upkeep 896 · charges 144 · occupation 15 · laws 300
- DISPATCH: Sire — 7 turns without settlement on Marshal Lannes. A rente would close it today; the arrears will not close themselves.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 14 — Early April 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Tyrol and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 2 actions unused) Turn 15 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 16322 · net +2251 · threat 45 · provinces 29 (+0) · ceiling 203833 · army 114632 · vassals Holland 97 · Kingdom of Italy 95 · Switzerland 91
  - NET income 2719 · trade 623 · admin 50 · tribute 225 · upkeep 880 · charges 171 · occupation 15 · laws 300
- DISPATCH: Sire — the levy has stood open 4 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 8
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 15 — Late April 1806
  - MAILBOX #13 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #20 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 3 actions unused) Turn 16 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: drill×1, wait×1
- LEDGER treasury 18351 · net +2004 · threat 45 · provinces 29 (+0) · ceiling 185333 · army 113753 · vassals Holland 96 · Kingdom of Italy 94 · Switzerland 100
  - NET income 2722 · trade 623 · admin 50 · upkeep 880 · charges 196 · occupation 15 · laws 300
- DISPATCH: Sire — Marshal Lannes's claim is 9 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 6
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG ai_ai_proposal_refused: 9 courts rebuff Austria (defensive alliance)

## Turn 16 — Early May 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `Ney, move to Bohemia` → ✓ Ney moves from Franconia to Bohemia (126 lost to march)
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Bohemia. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action unused) Turn 17 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×1
- LEDGER treasury 20358 · net +1983 · threat 45 · provinces 29 (+0) · ceiling 185583 · army 113143 · vassals Holland 95 · Kingdom of Italy 93 · Switzerland 100
  - NET income 2725 · trade 623 · admin 50 · upkeep 880 · charges 220 · occupation 15 · laws 300
- DISPATCH: Sire — Marshal Lannes's claim is 10 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 6
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Prussia (defensive alliance)

## Turn 17 — Late May 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Bohemia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mo…
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Tyrol (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 2 actions unused) Turn 18 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 22344 · net +2112 · threat 45 · provinces 29 (+0) · ceiling 198333 · army 112669 · vassals Holland 94 · Kingdom of Italy 92 · Switzerland 100
  - NET income 2728 · trade 623 · admin 50 · tribute 150 · upkeep 880 · charges 244 · occupation 15 · laws 300
- DISPATCH: Sire — the levy has stood open 7 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 6
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Britain and Russia (defensive alliance)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 18 — Early June 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Franconia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 4 actions unused) Turn 19 begins!
- enemy phase: 5 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2, recruit×2, garrison×1
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 24467 · net +2098 · threat 45 · provinces 29 (+0) · ceiling 199250 · army 112205 · vassals Holland 93 · Kingdom of Italy 91 · Switzerland 100
  - NET income 2731 · trade 623 · admin 50 · tribute 150 · upkeep 872 · charges 269 · occupation 15 · laws 300
- DISPATCH: Sire — Marshal Lannes's claim is 12 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 19 — Late June 1806
  - MAILBOX #14 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #21 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (1200g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Bohemia. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✓ Lannes moves from Bohemia to Franconia (110 lost to march)
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 3 actions unused) Turn 20 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 26442 · net +2288 · threat 45 · provinces 29 (+0) · ceiling 217083 · army 111268 · vassals Holland 92 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2734 · trade 623 · admin 50 · tribute 337 · upkeep 848 · charges 293 · occupation 15 · laws 300
- DISPATCH: Sire — Marshal Lannes's claim is 13 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 20 — Early July 1806
- CMD `enact the Staff` → ✗ The Grand Quartier Général is already in force (since turn 7).
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 4 actions unused) Turn 21 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 28733 · net +2264 · threat 43 · provinces 29 (+0) · ceiling 217333 · army 110458 · vassals Holland 91 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2737 · trade 623 · admin 50 · tribute 337 · upkeep 848 · charges 320 · occupation 15 · laws 300
- DISPATCH: Sire — the levy has stood open 10 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 4
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 21 — Late July 1806
  - MAILBOX #15 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #22 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 3 actions unused) Turn 22 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×1, wait×1
- LEDGER treasury 30663 · net +1907 · threat 41 · provinces 29 (+0) · ceiling 189500 · army 109664 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2740 · trade 623 · admin 50 · upkeep 848 · charges 343 · occupation 15 · laws 300
- DISPATCH: Sire — Marshal Lannes's claim is 15 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 6
- COURTS: The court of Sweden eases over Scourge of the Usurper — service to the strong is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 9 courts rebuff Austria (defensive alliance)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 3 actions unused) Turn 23 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 32578 · net +2117 · threat 39 · provinces 29 (+0) · ceiling 208916 · army 108886 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2740 · trade 623 · admin 50 · tribute 225 · upkeep 840 · charges 366 · occupation 15 · laws 300
- DISPATCH: Sire — Marshal Lannes's claim is 16 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 2 actions unused) Turn 24 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 34703 · net +2099 · threat 37 · provinces 29 (+0) · ceiling 209583 · army 108123 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2740 · trade 623 · admin 50 · tribute 225 · upkeep 832 · charges 392 · occupation 15 · laws 300
- DISPATCH: Sire — the levy has stood open 13 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 4 actions unused) Turn 25 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 36810 · net +2082 · threat 35 · provinces 29 (+0) · ceiling 210250 · army 107376 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2740 · trade 623 · admin 50 · tribute 225 · upkeep 824 · charges 417 · occupation 15 · laws 300
- DISPATCH: Sire — Marshal Lannes's claim is 18 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sweden and Austria (Defensive Alliance)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 2 actions unused) Turn 26 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 38900 · net +2065 · threat 33 · provinces 29 (+0) · ceiling 210916 · army 106643 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2740 · trade 623 · admin 50 · tribute 225 · upkeep 816 · charges 442 · occupation 15 · laws 300
- DISPATCH: Sire — Marshal Lannes's claim is 19 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 5 actions unused) Turn 27 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 40965 · net +2190 · threat 31 · provinces 29 (+0) · ceiling 223416 · army 105926 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2740 · trade 623 · admin 50 · tribute 375 · upkeep 816 · charges 467 · occupation 15 · laws 300
- DISPATCH: Sire — the levy has stood open 16 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 2 actions unused) Turn 28 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 43155 · net +2164 · threat 29 · provinces 29 (+0) · ceiling 223416 · army 105223 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2740 · trade 623 · admin 50 · tribute 375 · upkeep 816 · charges 493 · occupation 15 · laws 300
- DISPATCH: Sire — Marshal Lannes's claim is 21 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 4 actions unused) Turn 29 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 45343 · net +2498 · threat 27 · provinces 29 (+0) · ceiling 253500 · army 104533 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2740 · trade 623 · admin 50 · tribute 712 · upkeep 792 · charges 520 · occupation 15 · laws 300
- DISPATCH: Sire — Marshal Lannes's claim is 22 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 29 — Late November 1806
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. (Warning: 1 action unused) Turn 30 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 47841 · net +2468 · threat 25 · provinces 29 (+0) · ceiling 253500 · army 103857 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2740 · trade 623 · admin 50 · tribute 712 · upkeep 792 · charges 550 · occupation 15 · laws 300
- DISPATCH: Sire — the levy has stood open 19 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 4 courts rebuff Austria (non-aggression pact)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Bavaria (open borders agreement)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 4 actions unused) Turn 31 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 50309 · net +2439 · threat 23 · provinces 29 (+0) · ceiling 253500 · army 103195 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2740 · trade 623 · admin 50 · tribute 712 · upkeep 792 · charges 579 · occupation 15 · laws 300
- DISPATCH: Sire — Marshal Lannes's claim is 24 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Bohemia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mo…
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 2 actions unused) Turn 32 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 52748 · net +2410 · threat 21 · provinces 29 (+0) · ceiling 253500 · army 102546 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2740 · trade 623 · admin 50 · tribute 712 · upkeep 792 · charges 608 · occupation 15 · laws 300
- DISPATCH: Sire — Marshal Lannes's claim is 25 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Bohemia. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 4 actions unused) Turn 33 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 55166 · net +2389 · threat 19 · provinces 29 (+0) · ceiling 254166 · army 101910 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2740 · trade 623 · admin 50 · tribute 712 · upkeep 784 · charges 637 · occupation 15 · laws 300
- DISPATCH: Sire — the levy has stood open 22 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 33 — Late January 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 2 actions unused) Turn 34 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 57555 · net +2360 · threat 17 · provinces 29 (+0) · ceiling 254166 · army 101287 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2740 · trade 623 · admin 50 · tribute 712 · upkeep 784 · charges 666 · occupation 15 · laws 300
- DISPATCH: Sire — Marshal Lannes's claim is 27 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Tyrol. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 3 actions unused) Turn 35 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 59893 · net +2310 · threat 15 · provinces 29 (+0) · ceiling 252333 · army 100676 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2740 · trade 585 · admin 50 · tribute 712 · upkeep 768 · charges 694 · occupation 15 · laws 300
- DISPATCH: Sire — Marshal Lannes's claim is 28 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 2 actions unused) Turn 36 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 62211 · net +2290 · threat 13 · provinces 29 (+0) · ceiling 253000 · army 100078 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2740 · trade 585 · admin 50 · tribute 712 · upkeep 760 · charges 722 · occupation 15 · laws 300
- DISPATCH: Sire — the levy has stood open 25 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, law_lapsed_abroad)

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Bohemia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot mo…
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Tyrol. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Can…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 3 actions unused) Turn 37 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 64501 · net +2262 · threat 11 · provinces 29 (+0) · ceiling 253000 · army 99492 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2740 · trade 585 · admin 50 · tribute 712 · upkeep 760 · charges 750 · occupation 15 · laws 300
- DISPATCH: Sire — Marshal Lannes's claim is 30 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 9 courts rebuff Austria (open borders agreement)
  - LOG ai_ai_proposal_refused: 9 courts rebuff Bavaria (open borders agreement)

## Turn 37 — Late March 1807
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 3 actions unused) Turn 38 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 66763 · net +2235 · threat 9 · provinces 29 (+0) · ceiling 253000 · army 98918 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2740 · trade 585 · admin 50 · tribute 712 · upkeep 760 · charges 777 · occupation 15 · laws 300
- DISPATCH: Sire — Marshal Lannes's claim is 31 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- DIPLO +2 medium/low (diplomatic_dp_regen, law_lapsed_abroad)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Bavaria (open borders agreement)

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Bohemia. Army is now mobile.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 4 actions unused) Turn 39 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- LEDGER treasury 68998 · net +2209 · threat 7 · provinces 29 (+0) · ceiling 253000 · army 98355 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2740 · trade 585 · admin 50 · tribute 712 · upkeep 760 · charges 803 · occupation 15 · laws 300
- DISPATCH: Sire — the levy has stood open 28 turns. 150 gold puts 10,000 foot in the line at Paris, where a marshal must stand to receive them; the conscripts do not improve with keeping.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 7 courts rebuff Bavaria (open borders agreement)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 3 actions unused) Turn 40 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 71223 · net +2198 · threat 5 · provinces 29 (+0) · ceiling 254333 · army 97803 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2740 · trade 585 · admin 50 · tribute 712 · upkeep 744 · charges 830 · occupation 15 · laws 300
- DISPATCH: Sire — Marshal Lannes's claim is 33 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Bohemia. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Tyrol (+2% defense).
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 4 actions unused) Turn 41 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×2
- ENVOYS WAITING 1 · Sweden defensive alliance
- LEDGER treasury 73421 · net +2171 · threat 3 · provinces 29 (+0) · ceiling 254333 · army 97262 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2740 · trade 585 · admin 50 · tribute 712 · upkeep 744 · charges 857 · occupation 15 · laws 300
- DISPATCH: Sire — Marshal Lannes's claim is 34 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_ai_proposal: An envoy from Sweden has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: KingdomOfItaly rebuffs Bavaria (open borders agreement)

---
finished: **completed** · commands 220 · popups 47 · battles 16
