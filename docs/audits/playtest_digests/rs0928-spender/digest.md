# Playtest digest — rs0928-spender

seed `historical` · llm `mock` · transport in-process · policy `{"objection": "trust", "diplomacy": "accept", "capture": "secure", "estate": "respect", "glorious_charge": "restrain", "diplomatic_objection": "proceed", "redemption": "grant_autonomy", "petition": "first_enabled", "audience": "open", "declare_war": "cancel", "interrupt": "first", "last_stand": "first", "contact": "first", "paradox": "honor", "rebellion": "accept", "sabotage": "confront", "reward": "ignore", "war_purpose": "1", "ultimatum": "defy", "clarification": "first"}`
- played: board `The Third Coalition, 1805` · map `europe` (126 provinces) · France from turn 1 · campaign seed `historical` · dice `historical`
- platform: CPython 3.13.12 · Windows-11-10.0.22000-SP0 (AMD64) · PYTHONHASHSEED `0` · engine `91796f250248` · content `8f597da58501` · driver `aef52ad7cbfd`
  - new game → New campaign started. Autosave refreshed.

## Turn 1 — Late September 1805
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
- CMD `Ney, attack Mack` → ✓ MUSTER — Ney (19,554; expect about 50,708 with the corps likely to arrive, up to 51,946 if all march) vs Mack (14,689 men) at Tyrol — the balance of force looks favorabl…
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 631, own corps) vs Mack (lost 5976, own corps) — Massena's timely arrival bolstered Ney's position. Well-coordinated, Sire.
  - POPUP capture_choice[capture]: Tyrol, Ney → secure
- CMD `Davout, attack Mack` → ✗ Davout is recovering from retreat and cannot attack. Recovery: 1 turn remaining.
- CMD `Lannes, move to Swabia` → ✓ Lannes moves from Rhineland to Swabia (166 lost to march)
- CMD `recruit 10000 infantry with Soult` → ✓ Soult recruits 3,000 infantry at Lorraine (field levy — no depot; capped at 3,000) - Cost: 700 gold (×3 at war) (×1.17 over the ordinance). Morale: 100% -> 94%
- CMD `buy 30,000 substitutes for Ney` → ✗ Berthier shakes his head. 'Substitutes are 3,340 gold the battalion, Sire — 10,020 for 3. The treasury holds 2,118.'
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
- CMD `Ney, drill` → ✗ Ney cannot drill with enemy forces nearby! Archduke Charles is at Bohemia, just one region away.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, fortify` → ✓ Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archd…
  - POPUP objection: Lannes, Lannes respectfully raises concerns: 'I would rather attack than sit idle.' (Insisting costs 2 actions — he must first go defensive.) (Trust him and he will attack Archduke Charles at Bohemia instead.) → trust
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Lannes (lost 619, own corps) vs Archduke Charles (lost 5529) — Reinforcements! Ney, Massena and Napoleon marched onto the field beside Lannes. The enemy's advantage melted away.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `buy 30,000 substitutes for Soult` → ✗ Berthier shakes his head. 'Substitutes are 2,880 gold the battalion, Sire — 8,640 for 3. The treasury holds 7,715. We could stand 2 batches at that price.'
- CMD `end turn` → ✓ Turn 6 ended. (Warning: 3 actions unused) Turn 7 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 9353 · net +1426 · threat 93 · provinces 29 (+0) · ceiling 21391 · army 126614 · vassals Holland 97 · Kingdom of Italy 97 · Switzerland 97
  - NET income 2616 · trade 587 · admin 50 · tribute 487 · upkeep 984 · charges 870 · requisitions 50 · occupation 52 · blockade 368 · admiralty 90
- DISPATCH: Sire — Leon has been taken by Britain.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 7 — Late December 1805
- CMD `Ney, attack Archduke Charles` → ✓ MUSTER — Ney (14,925; expect about 36,430 with the corps likely to arrive, up to 39,825 if all march) vs Archduke Charles (substantial force) at Vienna — the balance of …
  - POPUP battle_diorama: (no summary fields) → display-only
  - ⚔ Ney (lost 642, own corps) vs Archduke Charles (lost 4379, own corps) — Reinforcements! Lannes, Massena and Napoleon marched onto the field beside Ney. The enemy's advantage melted away.
- CMD `Davout, move to Bohemia` → ✓ Davout begins marching to Bohemia (distance: 3). Moved to Swabia. Route: Swabia -> Franconia -> Bohemia.
- CMD `Murat, attack Archduke Charles` → ✗ Not enough actions for a strategic pursuit! Need 2, have 1.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 7 ended. (Warning: 1 action unused) Turn 8 begins!
- enemy phase: 6 actions, 0 attacks — Britain, Russia, Prussia and 5 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, retreat×1, stance_change×1, move×1, wait×1
- ORDER Davout [active]: Davout is marching to Bohemia (3 turns remaining).
  - POPUP marshal_petition: jealousy_confrontation, Marshal Massena demands to be heard → acknowledge
  -     ↳ Massena's grievance runs its course.
- LEDGER treasury 10747 · net +1309 · threat 94 · provinces 29 (+0) · ceiling 21366 · army 119656 · vassals Holland 98 · Kingdom of Italy 98 · Switzerland 97
  - NET income 2617 · trade 587 · admin 50 · tribute 487 · upkeep 920 · charges 1077 · requisitions 75 · occupation 52 · blockade 368 · admiralty 90
- DISPATCH: Supply cost you 4,160 men, at Vienna and Swabia.
  - TURN EVENTS 7
- DIPLO +2 medium/low (diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG sponsorship_granted: Russia sponsors Austria against France (200g/turn)
  - LOG ai_ai_proposal_refused: Britain and Prussia rebuff Bavaria (open borders agreement)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Austria (non-aggression pact)

## Turn 8 — Early January 1806
- CMD `Davout, attack Archduke Charles` → ✗ No intelligence on Archduke Charles's position, Sire. Scout for him before Davout can give chase.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Ney fortifies position at Vie…
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 9, and he remains at your orders (though he cannot shift…
- CMD `Massena, move to Milan` → ✗ Not enough actions for a strategic march! Need 2, have 1.
- CMD `end turn` → ✓ Turn 8 ended. (Warning: 1 action unused) Turn 9 begins!
- enemy phase: 10 actions, 4 attacks — Russia, Austria, Prussia and 4 other courts stirred as well, but their formations remain beyond our sight. — Castanos attacks with overwhelming force. Castanos gains the advantage over Paget. Casualties: Castanos 720, Paget 1,58… · Deroy assaults the Munich garrison! Garrison: 10,000 -> 6,935 (-3,065). Deroy loses 3,472 troops. Garrison holds — 6,93… · Deroy assaults the Munich garrison! Garrison collapses (6,935 -> 0). Deroy loses 2,675 troops in the assault. Deroy mar… · Deroy marches from Munich into Franconia unopposed! (58 lost to march) Captured: Austria → Bavaria
  - 🏴 Bavaria: [Materiel] Guns, horses and stores lost with the fallen: Bavaria -133g, Austria -98g. Captured: Austria → Bavaria
  - 🏴 Bavaria: Deroy marches from Munich into Franconia unopposed! (58 lost to march) Captured: Austria → Bavaria
  - ⚔ Castanos (lost 720) vs Paget (lost 1586) — An aggressive stance invites disaster when one is not the attacker, Sire. Paget paid the price.
  - verbs: move×4, attack×4, unfortify×1, wait×1
- ORDER Davout : Davout: 'Cannon fire at Munich, Sire. Investigate?'
  - ⚡ AUTONOMOUS: [Combat] Massena leads the charge! (Aggressive: +15% attack)
  - ⚔ Massena (lost 687, own corps) vs Archduke John (lost 2396, own corps) — Lannes and Napoleon arrived to reinforce Massena! The timely arrival swung the battle in our favor, Sire.
  - POPUP strategic_interrupt: Davout, cannon_fire, Davout: 'Cannon fire at Munich, Sire. Investigate?' → investigate
  - POPUP capture_choice[capture]: Moravia, Massena → secure
- ENVOYS WAITING 1 · Austria armistice losing
- LEDGER treasury 11928 · net +1005 · threat 97 · provinces 30 (+1) · ceiling 19847 · army 115663 · vassals Holland 99 · Kingdom of Italy 99 · Switzerland 97
  - NET income 2661 · trade 587 · admin 50 · tribute 487 · upkeep 896 · charges 1258 · contributions 138 · requisitions 75 · occupation 105 · blockade 368 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Berry. No French corps stands in his path.
  - RAIL diplomatic_ai_proposal: An envoy from Austria has arrived with a proposal.
  - RAIL design_promoted: REVANCHE: Austria will not forgive France the loss of Moravia and 1 more province. A new design hardens in their court.
  - TURN EVENTS 6
- DIPLO +4 medium/low (law_enacted_abroad, diplomatic_dp_regen, paymaster_subsidy, agenda_shift)
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
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Vienna. Army is now mobile.
- CMD `Lannes, move to Bohemia` → ✗ Cannot enter Bohemia — the evacuation corridor with Austria grants safe passage HOME to stranded corps, not entry. Lannes can already reach the body of the realm from wh…
- CMD `Murat, drill` → ✓ Murat begins intensive drill exercises at Swabia. Troops will be locked in training next turn, bonus ready turn 11.
- CMD `recruit 10000 cavalry with Murat` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `buy 30,000 substitutes for Davout` → ✓ Davout takes 30,000 substitutes into the line at Munich — 7,467 gold, and not a man off the rolls. Morale 12% -> 20% (bought men muster at 25%). The going rate is 4.9 ti…
- CMD `end turn` → ✓ Turn 9 ended. (Warning: 2 actions unused) Turn 10 begins!
- SPENT 7467g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Ney [completed]: Ney arrives at Moravia. Ney: "Accomplished. The men want a battle, not another road."
- ENVOYS WAITING 2 · Britain settlement offer · KingdomOfItaly client petition
- LEDGER treasury 6155 · net +1491 · threat 95 · provinces 30 (+0) · ceiling 17623 · army 143883 · vassals Holland 99 · Kingdom of Italy 97 · Switzerland 96
  - NET income 2701 · trade 587 · admin 50 · tribute 487 · upkeep 1214 · charges 540 · contributions 40 · occupation 82 · blockade 368 · admiralty 90
- DISPATCH: Sire — Paget has crossed into Normandy. No French corps stands in his path.
  - RAIL armistice_ratified: A truce with Austria: the fighting stops for 5 turns — peace if relations heal to -60 or better, else the war resumes.
  - RAIL settlement_offer_arrival: Britain has offered terms to settle France vs Britain.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 6
- COURTS: The court of Austria eases over Revanche — an ultimatum is now the length of its tether.
- DIPLO +5 medium/low (diplomatic_treaty_signed, law_enacted_abroad ×2, diplomatic_dp_regen, paymaster_subsidy)
  - LOG british_subsidy: Britain's gold: 200g reaches Austria
  - LOG ai_ai_proposal_refused: 9 courts rebuff Austria (defensive alliance)
  - LOG design_promoted: REVANCHE: Austria swears to retake Moravia and 1 more — France is not forgiven
  - LOG ai_ai_proposal_refused: 16 approaches from Bavaria and Austria are rebuffed (open borders agreement)

## Turn 10 — Early February 1806
  - MAILBOX #10 Britain incoming_settlement_offer: Britain — Settlement Offer → activated
  - MAILBOX #11 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: incoming_settlement_offer #12 → accept_settlement_offer
  -     ↳ refused: Sire, another matter has arrived since — this concerns Kingdom Of Italy. Your earlier answer was not delivere…
  - POPUP diplomatic_dialogue: incoming_proposal #13 → grant the petition
  - POPUP diplomatic_dialogue: incoming_settlement_offer #12 → accept_settlement_offer
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (1200g forgone). Loyalty +3 (97 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
  - POPUP diplomatic_dialogue: settlement_confirm #14 → confirm_settlement
  - POPUP proposal_result: Settlement Ratified, Settlement Ratified: France vs Austria + Britain + Russia (7 pairs resolved). Status quo: Moravia and Tyrol stay ours by the treaty — titled. Status quo: Leon stays British by the treaty. Status quo: Milan stays Austrian by the treaty. → display-only
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #13 → grant the petition
  -     ↳ refused: No diplomatic matter awaits your attention, Sire.
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, move to Franconia` → ✓ Ney begins marching to Franconia (distance: 2). Moved to Dresden. Route: Dresden -> Franconia.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Munich. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fortifi…
- CMD `Soult, move to Bavaria` → ✗ Bavaria is a nation, not a province. Name a province, Sire — theirs are Franconia, Munich, Swabia.
- CMD `end turn` → ✓ Turn 10 ended. (Warning: 1 action unused) Turn 11 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ORDER Ney [active]: Ney is marching to Franconia (2 turns remaining).
  - POPUP marshal_petition: rivalry_confrontation, A rivalry among the marshals → accept_breach
  -     ↳ Murat and Ney: They settle into cold war.
  - POPUP diplomatic_dialogue: Holland, client_petition #15 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +3 (97 → 100); bond 0 → 20 (+1 a turn). Cost: 1 DP. → display-only
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 8282 · net +1701 · threat 47 · provinces 30 (+0) · ceiling 48761 · army 147880 · vassals Holland 100 · Kingdom of Italy 99 · Switzerland 95
  - NET income 2707 · trade 623 · admin 50 · upkeep 1334 · charges 263 · occupation 82
- DISPATCH: Sire — the war with Britain is over. The peace grants safe passage home.
  - RAIL settlement_summary: Settlement of France + Spain + Holland + Bavaria + Kingdom of Italy vs Britain + Austria + Russia: settlement ratified.
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - RAIL strait_open: THE STRAIT: the Cagliari–Corsica crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the Corsica–Piedmont crossing stands open to our armies.
  - RAIL strait_open: THE STRAIT: the London–Normandy crossing stands open to our armies.
  - TURN EVENTS 8
- COURTS: The court of Russia eases over Arbiter of Europe — an ultimatum is now the length of its tether.
- COURTS: The court of Sweden eases over Scourge of the Usurper — an ultimatum is now the length of its tether.
- COURTS: And 3 other courts stir at their own designs.
- DIPLO +6 medium/low (diplomatic_coalition_dissolved, status_quo_titled, diplomatic_dp_regen, blockade_broken ×3)
  - LOG ai_ai_proposal_refused: 15 approaches from Britain, Russia and Prussia are rebuffed (defensive alliance)
  - LOG coalition_member_left: Britain has left the coalition.
  - LOG coalition_member_left: Austria has left the coalition.
  - LOG coalition_dissolved: Coalition against France has dissolved — the league is spent; Europe's alarm falls from 95 to 47.
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Bavaria (open borders agreement)

## Turn 11 — Late February 1806
- CMD `Ney, attack Archduke John` → ✗ We are not at war with Austria, Sire — Archduke John may not be attacked while the peace holds. Declare war on Austria first, or leave him be.
- CMD `Lannes, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #16 → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation #17 → reconsider
- CMD `Murat, move to Franconia` → ✓ Murat moves from Swabia to Franconia (224 lost to march)
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Massena fortifies positio…
- CMD `end turn` → ✓ Turn 11 ended. Turn 12 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- ORDER Ney [completed]: Ney arrives at Franconia. Ney: "Done — and I trust the next order has more fire in it."
- LEDGER treasury 10311 · net +2005 · threat 47 · provinces 30 (+0) · ceiling 177333 · army 146047 · vassals Holland 99 · Kingdom of Italy 98 · Switzerland 94
  - NET income 2787 · trade 623 · admin 50 · upkeep 1296 · charges 99 · occupation 60
- DISPATCH: Sire — Marshal Lannes's household goes unpaid. His patience erodes with his purse.
  - TURN EVENTS 2
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Austria, Naples and Denmark rebuff Bavaria (open borders agreement)
  - LOG sponsorship_expired: The compact between Britain and Russia lapses

## Turn 12 — Early March 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 14.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Soult, fortify` → ✓ [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max…
- CMD `recruit 10000 infantry with Lannes` → ✓ Lannes recruits 3,000 infantry at Moravia (field levy — no depot; capped at 3,000) - Cost: 324 gold (unstable region premium) (×1.08 over the ordinance). Morale: 75% -> …
- CMD `buy 30,000 substitutes for Lannes` → ✓ Lannes takes 9,000 substitutes into the line at Moravia — 3,972 gold, and not a man off the rolls. Morale 67% -> 50% (bought men muster at 25%). They come up in drafts o…
- CMD `end turn` → ✓ Turn 12 ended. (Warning: 1 action unused) Turn 13 begins!
- SPENT 4296g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 7728 · net +1743 · threat 47 · provinces 30 (+0) · ceiling 152916 · army 156359 · vassals Holland 98 · Kingdom of Italy 97 · Switzerland 93
  - NET income 2794 · trade 623 · admin 50 · upkeep 1596 · charges 68 · occupation 60
- DISPATCH: Sire — Marshal Lannes has now gone unrewarded 6 turns. The staff have noticed which of us he no longer looks at.
  - TURN EVENTS 6
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses
  - LOG ai_ai_proposal_refused: 9 approaches from Britain, Russia and Prussia are rebuffed (defensive alliance)

## Turn 13 — Late March 1806
- CMD `Ney, attack Archduke John` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 13.
- CMD `Murat, attack Archduke John` → ✓ Choose your war purpose against Austria. Issue the attack again after the declaration is settled.
  - POPUP diplomatic_dialogue: war_purpose_selection #18 → 1
  - POPUP diplomatic_dialogue: force_declare_war_confirmation #19 → reconsider
- CMD `Davout, move to Franconia` → ✓ Davout moves from Munich to Franconia (1,289 lost to march)
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `end turn` → ✓ Turn 13 ended. (Warning: 2 actions unused) Turn 14 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 9670 · net +2143 · threat 47 · provinces 30 (+0) · ceiling 188250 · army 151428 · vassals Holland 97 · Kingdom of Italy 96 · Switzerland 92
  - NET income 2828 · trade 623 · admin 50 · tribute 225 · upkeep 1446 · charges 92 · occupation 45
- DISPATCH: Sire — Ney, Davout and Murat stand 70,783 men at Franconia, which feeds 60,000. 10,783 too many. 4,026 men lost in 3 turns. Bavaria's magazines feed us as our own — the army is simply too large for t…
  - TURN EVENTS 3
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (400g/turn)

## Turn 14 — Early April 1806
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Lannes fortifies position …
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Massena, move to Tyrol` → ✗ Massena is fortified at Moravia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 14 ended. (Warning: 1 action unused) Turn 15 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- ENVOYS WAITING 1 · Switzerland client petition
- LEDGER treasury 11989 · net +2292 · threat 47 · provinces 30 (+0) · ceiling 202916 · army 147964 · vassals Holland 96 · Kingdom of Italy 95 · Switzerland 91
  - NET income 2869 · trade 623 · admin 50 · tribute 225 · upkeep 1326 · charges 119 · occupation 30
- DISPATCH: Sire — Ney, Davout and Murat stand 68,226 men at Franconia, which feeds 60,000. 8,226 too many. 5,921 men lost in 3 turns. Bavaria's magazines feed us as our own — the army is simply too large for th…
  - RAIL diplomatic_ai_proposal: An envoy from Switzerland has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 15 — Late April 1806
  - MAILBOX #13 Switzerland incoming_proposal: Switzerland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Switzerland, client_petition #20 → grant the petition
  - POPUP proposal_result: Switzerland's tribute is remitted for 8 collections (1800g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 17.
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `buy 30,000 substitutes for Massena` → ✓ Massena takes 9,000 substitutes into the line at Moravia — 3,021 gold, and not a man off the rolls. Morale 48% -> 40% (bought men muster at 25%). They come up in drafts …
- CMD `end turn` → ✓ Turn 15 ended. (Warning: 2 actions unused) Turn 16 begins!
- SPENT 3021g on this turn's orders
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 10861 · net +1895 · threat 47 · provinces 30 (+0) · ceiling 168750 · army 153379 · vassals Holland 95 · Kingdom of Italy 94 · Switzerland 100
  - NET income 2872 · trade 623 · admin 50 · upkeep 1514 · charges 106 · occupation 30
- DISPATCH: Sire — Marshal Lannes's claim is 9 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 8
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 9 courts rebuff Austria (defensive alliance)

## Turn 16 — Early May 1806
- CMD `Ney, move to Bohemia` → ✗ Cannot enter Bohemia — it is controlled by Austria (diplomatic state: PEACE). Open borders or higher required.
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Moravia. Army is now mobile.
- CMD `Murat, fortify` → ✓ Murat grumbles about defensive orders but complies. [Auto-shifted to DEFENSIVE stance first — cost 2 AP: 1 for stance change + 1 for fortify] Murat fortifies position at…
- CMD `Soult, move to Franconia` → ✗ Soult is fortified at Swabia and cannot move. Order 'unfortify' first to make the army mobile.
- CMD `end turn` → ✓ Turn 16 ended. (Warning: 1 action unused) Turn 17 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: recruit×2, wait×1
- LEDGER treasury 12895 · net +2010 · threat 47 · provinces 30 (+0) · ceiling 180333 · army 149863 · vassals Holland 94 · Kingdom of Italy 93 · Switzerland 100
  - NET income 2875 · trade 623 · admin 50 · upkeep 1378 · charges 130 · occupation 30
- DISPATCH: Sire — Ney, Davout and Murat have been 4 turns over what Franconia can feed. 7,541 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply too large…
  - TURN EVENTS 4
- DIPLO +3 medium/low (law_enacted_abroad ×2, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 9 approaches from Britain, Russia and Prussia are rebuffed (defensive alliance)

## Turn 17 — Late May 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Moravia. Troops will be locked in training next turn, bonus ready turn 19.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Moravia (+1% defense).
- CMD `end turn` → ✓ Turn 17 ended. (Warning: 1 action unused) Turn 18 begins!
- enemy phase: 3 actions, 0 attacks — Britain, Russia, Austria and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: garrison×1, wait×1, recruit×1
- LEDGER treasury 14982 · net +2212 · threat 47 · provinces 30 (+0) · ceiling 199250 · army 146514 · vassals Holland 93 · Kingdom of Italy 92 · Switzerland 100
  - NET income 2878 · trade 623 · admin 50 · tribute 150 · upkeep 1304 · charges 155 · occupation 30
- DISPATCH: Sire — Ney, Davout and Murat have been 5 turns over what Franconia can feed. 7,306 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply too large…
  - TURN EVENTS 6
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 18 — Early June 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, drill` → ✗ Soult is fortified and cannot drill. Abandon fortification first.
- CMD `Murat, unfortify` → ✓ Murat abandons fortified position at Franconia. Army is now mobile.
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `buy 30,000 substitutes for Ney` → ✓ Ney takes 9,000 substitutes into the line at Franconia — 2,994 gold, and not a man off the rolls. Morale 75% -> 51% (bought men muster at 25%). They come up in drafts of…
- CMD `end turn` → ✓ Turn 18 ended. (Warning: 3 actions unused) Turn 19 begins!
- SPENT 2994g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · KingdomOfItaly client petition
- LEDGER treasury 14042 · net +2391 · threat 47 · provinces 30 (+0) · ceiling 213250 · army 152938 · vassals Holland 92 · Kingdom of Italy 91 · Switzerland 100
  - NET income 2881 · trade 623 · admin 50 · tribute 487 · upkeep 1476 · charges 144 · occupation 30
- DISPATCH: Sire — Marshal Lannes's claim is 12 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_ai_proposal: An envoy from the Kingdom of Italy has arrived with a petition.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (300g/turn)

## Turn 19 — Late June 1806
  - MAILBOX #14 KingdomOfItaly incoming_proposal: Kingdom of Italy — Client's Petition → activated
  - POPUP diplomatic_dialogue: KingdomOfItaly, client_petition #21 → grant the petition
  - POPUP proposal_result: The Kingdom of Italy's tribute is remitted for 8 collections (1200g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, move to Franconia` → ✓ Lannes begins marching to Franconia (distance: 2). Moved to Dresden. Route: Dresden -> Franconia.
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 19 ended. (Warning: 1 action unused) Turn 20 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ORDER Lannes [active]: Lannes is marching to Franconia (2 turns remaining).
- ENVOYS WAITING 1 · Holland client petition
- LEDGER treasury 16316 · net +2247 · threat 45 · provinces 30 (+0) · ceiling 203500 · army 151164 · vassals Holland 91 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2884 · trade 623 · admin 50 · tribute 337 · upkeep 1446 · charges 171 · occupation 30
- DISPATCH: Sire — Ney, Davout and Murat have been 7 turns over what Franconia can feed. 5,401 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply too large…
  - RAIL diplomatic_ai_proposal: An envoy from Holland has arrived with a petition.
  - TURN EVENTS 3
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 6 courts rebuff Austria (non-aggression pact)
  - LOG ai_ai_proposal_refused: Prussia rebuffs Bavaria (open borders agreement)

## Turn 20 — Early July 1806
  - MAILBOX #15 Holland incoming_proposal: Holland — Client's Petition → activated
  - POPUP diplomatic_dialogue: Holland, client_petition #22 → grant the petition
  - POPUP proposal_result: Holland's tribute is remitted for 8 collections (2696g forgone). Loyalty +9 (91 → 100); bond 20 → 40 (+2 a turn). Cost: 1 DP. → display-only
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 22.
- CMD `Soult, fortify` → ✗ Soult is already fortified at Swabia (+11% defense).
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `end turn` → ✓ Turn 20 ended. (Warning: 3 actions unused) Turn 21 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ORDER Lannes [completed]: Lannes arrives at Franconia. Lannes: "Done — and I trust the next order has more fire in it."
- LEDGER treasury 18357 · net +2016 · threat 43 · provinces 30 (+0) · ceiling 186333 · army 147430 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2887 · trade 623 · admin 50 · upkeep 1318 · charges 196 · occupation 30
- DISPATCH: Sire — Ney, Davout, Lannes and Murat have been 8 turns over what Franconia can feed. 6,219 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply t…
  - TURN EVENTS 4
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Naples rebuffs Prussia (defensive alliance)

## Turn 21 — Late July 1806
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 21.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 23.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `buy 30,000 substitutes for Soult` → ✓ Soult takes 9,000 substitutes into the line at Swabia — 2,619 gold, and not a man off the rolls. Morale 100% -> 82% (bought men muster at 25%). They come up in drafts of…
- CMD `end turn` → ✓ Turn 21 ended. (Warning: 2 actions unused) Turn 22 begins!
- SPENT 2619g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 17576 · net +1841 · threat 41 · provinces 30 (+0) · ceiling 170916 · army 153470 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2890 · trade 623 · admin 50 · upkeep 1506 · charges 186 · occupation 30
- DISPATCH: Sire — Marshal Lannes's claim is 15 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 6
- COURTS: The court of Sweden eases over Scourge of the Usurper — service to the strong is now the length of its tether.
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: 9 courts rebuff Austria (defensive alliance)
  - LOG ai_ai_proposal_refused: 8 courts rebuff Bavaria (open borders agreement)

## Turn 22 — Early August 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Moravia. Army is now mobile.
- CMD `end turn` → ✓ Turn 22 ended. (Warning: 2 actions unused) Turn 23 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 19507 · net +2132 · threat 39 · provinces 30 (+0) · ceiling 197166 · army 150674 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2890 · trade 623 · admin 50 · tribute 225 · upkeep 1416 · charges 210 · occupation 30
- DISPATCH: Sire — Ney, Davout, Lannes and Murat have been 10 turns over what Franconia can feed. 8,896 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply …
  - TURN EVENTS 3
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)

## Turn 23 — Late August 1806
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 24, and he remains at your orders (though he cannot shif…
- CMD `end turn` → ✓ Turn 23 ended. (Warning: 1 action unused) Turn 24 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 21707 · net +2174 · threat 37 · provinces 30 (+0) · ceiling 202833 · army 148030 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2890 · trade 623 · admin 50 · tribute 225 · upkeep 1348 · charges 236 · occupation 30
- DISPATCH: Sire — Ney, Davout, Lannes and Murat have been 11 turns over what Franconia can feed. 8,400 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply …
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 24 — Early September 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Moravia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `buy 30,000 substitutes for Davout` → ✓ Davout takes 9,000 substitutes into the line at Franconia — 2,235 gold, and not a man off the rolls. Morale 40% -> 36% (bought men muster at 25%). They come up in drafts…
- CMD `end turn` → ✓ Turn 24 ended. (Warning: 3 actions unused) Turn 25 begins!
- SPENT 2235g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 21460 · net +1989 · threat 35 · provinces 30 (+0) · ceiling 187166 · army 154035 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2890 · trade 623 · admin 50 · tribute 225 · upkeep 1536 · charges 233 · occupation 30
- DISPATCH: Sire — Marshal Lannes's claim is 18 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_ai_ai_treaty)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)
  - LOG diplomatic_ai_ai_treaty: AI-AI treaty: Sweden and Austria (Defensive Alliance)

## Turn 25 — Late September 1806
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 27.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 25 ended. (Warning: 1 action unused) Turn 26 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 23547 · net +2062 · threat 33 · provinces 30 (+0) · ceiling 195333 · army 151208 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2890 · trade 623 · admin 50 · tribute 225 · upkeep 1438 · charges 258 · occupation 30
- DISPATCH: Sire — Ney, Davout, Lannes and Murat have been 13 turns over what Franconia can feed. 8,466 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply …
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_ai_proposal_refused: Hanover, Papal States and Sardinia rebuff Austria (defensive alliance)

## Turn 26 — Early October 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, fortify` → ✗ Ney is locked in drill exercises and cannot receive orders. Training completes turn 26.
- CMD `end turn` → ✓ Turn 26 ended. (Warning: 4 actions unused) Turn 27 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 25699 · net +2276 · threat 31 · provinces 30 (+0) · ceiling 215333 · army 148536 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2890 · trade 623 · admin 50 · tribute 375 · upkeep 1348 · charges 284 · occupation 30
- DISPATCH: Sire — Ney, Davout, Lannes and Murat have been 14 turns over what Franconia can feed. 8,494 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply …
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 27 — Late October 1806
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 29.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `buy 30,000 substitutes for Lannes` → ✓ Lannes takes 9,000 substitutes into the line at Franconia — 2,640 gold, and not a man off the rolls. Morale 70% -> 53% (bought men muster at 25%). They come up in drafts…
- CMD `end turn` → ✓ Turn 27 ended. (Warning: 1 action unused) Turn 28 begins!
- SPENT 2640g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 25154 · net +2432 · threat 29 · provinces 30 (+0) · ceiling 227750 · army 154513 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2890 · trade 623 · admin 50 · tribute 712 · upkeep 1536 · charges 277 · occupation 30
- DISPATCH: Sire — Marshal Lannes's claim is 21 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +3 medium/low (law_enacted_abroad, diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: Austria–Russia (ALLIANCE → DEFENSIVE ALLIANCE)

## Turn 28 — Early November 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✗ Ney is not currently fortified.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Moravia. Army is now mobile.
- CMD `end turn` → ✓ Turn 28 ended. (Warning: 3 actions unused) Turn 29 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Sweden defensive alliance
- LEDGER treasury 27668 · net +2483 · threat 27 · provinces 30 (+0) · ceiling 234583 · army 151660 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2890 · trade 623 · admin 50 · tribute 712 · upkeep 1454 · charges 308 · occupation 30
- DISPATCH: Sire — Ney, Davout, Lannes and Murat have been 16 turns over what Franconia can feed. 8,548 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply …
  - RAIL diplomatic_ai_proposal: An envoy from Sweden has arrived with a proposal.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses
  - LOG ai_ai_proposal_refused: 8 approaches from Russia and Prussia are rebuffed (defensive alliance)

## Turn 29 — Late November 1806
  - MAILBOX #16 Sweden incoming_proposal: Sweden — Defensive Alliance → activated
  - POPUP diplomatic_dialogue: Sweden, defensive_alliance #23 → accept
  -     ↳ refused: Sweden's terms could not be ratified: Relations with France are insufficient for DEFENSIVE_ALLIANCE.
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 30, and he remains at your orders (though he cannot shif…
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 31.
- CMD `end turn` → ✓ Turn 29 ended. Turn 30 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 30249 · net +2551 · threat 25 · provinces 30 (+0) · ceiling 242750 · army 148962 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2890 · trade 623 · admin 50 · tribute 712 · upkeep 1356 · charges 338 · occupation 30
- DISPATCH: Sire — Ney, Davout, Lannes and Murat have been 17 turns over what Franconia can feed. 8,574 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply …
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (300g/turn)
  - LOG ai_proposal_rejected: We rejected Sweden's defensive alliance proposal
  - LOG ai_ai_proposal_refused: Sardinia rebuffs Prussia (defensive alliance)

## Turn 30 — Early December 1806
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Moravia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Davout` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `buy 30,000 substitutes for Massena` → ✓ Massena takes 9,000 substitutes into the line at Moravia — 3,042 gold, and not a man off the rolls. Morale 40% -> 35% (bought men muster at 25%). They come up in drafts …
- CMD `end turn` → ✓ Turn 30 ended. (Warning: 3 actions unused) Turn 31 begins!
- SPENT 3042g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 29559 · net +2349 · threat 23 · provinces 30 (+0) · ceiling 225250 · army 155409 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2890 · trade 623 · admin 50 · tribute 712 · upkeep 1566 · charges 330 · occupation 30
- DISPATCH: Sire — Marshal Lannes's claim is 24 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 31 — Late December 1806
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 33.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `end turn` → ✓ Turn 31 ended. (Warning: 1 action unused) Turn 32 begins!
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: move×1, recruit×1
- LEDGER treasury 31990 · net +2402 · threat 21 · provinces 30 (+0) · ceiling 232083 · army 152989 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2890 · trade 623 · admin 50 · tribute 712 · upkeep 1484 · charges 359 · occupation 30
- DISPATCH: Sire — Ney, Davout, Lannes and Murat have been 19 turns over what Franconia can feed. 7,671 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply …
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 32 — Early January 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `end turn` → ✓ Turn 32 ended. (Warning: 3 actions unused) Turn 33 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Sweden defensive alliance
- LEDGER treasury 34460 · net +2440 · threat 19 · provinces 30 (+0) · ceiling 237750 · army 150691 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2890 · trade 623 · admin 50 · tribute 712 · upkeep 1416 · charges 389 · occupation 30
- DISPATCH: Sire — Ney, Davout, Lannes and Murat have been 20 turns over what Franconia can feed. 7,271 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply …
  - RAIL diplomatic_ai_proposal: An envoy from Sweden has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 33 — Late January 1807
  - MAILBOX #17 Sweden incoming_proposal: Sweden — Defensive Alliance → activated
  - POPUP diplomatic_dialogue: Sweden, defensive_alliance #24 → accept
  -     ↳ refused: Sweden's terms could not be ratified: Relations with France are insufficient for DEFENSIVE_ALLIANCE.
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 35.
- CMD `Lannes, fortify` → ✓ Lannes grumbles about defensive orders but complies. Lannes fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `recruit 10000 infantry with Murat` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `buy 30,000 substitutes for Ney` → ✓ Ney takes 9,000 substitutes into the line at Franconia — 3,078 gold, and not a man off the rolls. Morale 81% -> 56% (bought men muster at 25%). They come up in drafts of…
- CMD `end turn` → ✓ Turn 33 ended. (Warning: 1 action unused) Turn 34 begins!
- SPENT 3078g on this turn's orders
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 33632 · net +2248 · threat 17 · provinces 30 (+0) · ceiling 220916 · army 157047 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2890 · trade 623 · admin 50 · tribute 712 · upkeep 1618 · charges 379 · occupation 30
- DISPATCH: Sire — Marshal Lannes's claim is 27 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 4
- DIPLO +2 medium/low (law_enacted_abroad, diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Sweden's defensive alliance proposal
  - LOG ai_ai_proposal_refused: Naples and Denmark rebuff Bavaria (open borders agreement)

## Turn 34 — Early February 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `Massena, unfortify` → ✓ Massena abandons fortified position at Moravia. Army is now mobile.
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 36.
- CMD `end turn` → ✓ Turn 34 ended. (Warning: 2 actions unused) Turn 35 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 35916 · net +2257 · threat 15 · provinces 30 (+0) · ceiling 223916 · army 154541 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2890 · trade 585 · admin 50 · tribute 712 · upkeep 1544 · charges 406 · occupation 30
- DISPATCH: Sire — Ney, Davout, Lannes and Murat have been 22 turns over what Franconia can feed. 7,448 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply …
  - TURN EVENTS 4
- DIPLO +2 medium/low (diplomatic_dp_regen, diplomatic_auto_downgrade)
  - LOG auto_downgrade: Relations auto-downgraded: France–Spain (ALLIANCE → DEFENSIVE ALLIANCE)
  - LOG sponsorship_expired: The compact between Britain and Austria lapses

## Turn 35 — Late February 1807
- CMD `Davout, fortify` → ✓ Davout fortifies position at Franconia. Defense bonus: +7% (grows +3% per turn, max 12%) (Iron Marshal: +5% instant, +3%/turn, max 12%). Cannot move or attack while fort…
- CMD `Lannes, unfortify` → ✓ Lannes abandons fortified position at Franconia. Army is now mobile.
- CMD `Soult, drill` → ✓ Soult drills his corps with Boulogne-camp precision at Swabia. Sharpen today, strike tomorrow — bonus ready turn 36, and he remains at your orders (though he cannot shif…
- CMD `Murat, drill` → ✗ Murat cannot drill while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `end turn` → ✓ Turn 35 ended. (Warning: 1 action unused) Turn 36 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 38249 · net +2305 · threat 13 · provinces 30 (+0) · ceiling 230250 · army 152166 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2890 · trade 585 · admin 50 · tribute 712 · upkeep 1468 · charges 434 · occupation 30
- DISPATCH: Sire — Ney, Davout, Lannes and Murat have been 23 turns over what Franconia can feed. 7,525 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply …
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Britain sponsors Austria against France (500g/turn)

## Turn 36 — Early March 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, fortify` → ✓ Ney grumbles about defensive orders but complies. Ney fortifies position at Franconia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). Cannot …
- CMD `Massena, fortify` → ✓ Massena grumbles about defensive orders but complies. Massena fortifies position at Moravia. Defense bonus: +2% (grows +2% per turn, max 8%) (Aggressive: max 8% only). C…
- CMD `recruit 10000 infantry with Soult` → ✗ Berthier frowns. 'We do not control Swabia, Your Majesty. Recruitment is impossible there.'
- CMD `buy 30,000 substitutes for Soult` → ✓ Soult takes 9,000 substitutes into the line at Swabia — 2,703 gold, and not a man off the rolls. Morale 100% -> 86% (bought men muster at 25%). They come up in drafts of…
- CMD `end turn` → ✓ Turn 36 ended. (Warning: 2 actions unused) Turn 37 begins!
- SPENT 2703g on this turn's orders
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Sweden defensive alliance
- LEDGER treasury 37678 · net +2131 · threat 11 · provinces 30 (+0) · ceiling 215250 · army 158911 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2890 · trade 585 · admin 50 · tribute 712 · upkeep 1648 · charges 428 · occupation 30
- DISPATCH: Sire — Marshal Lannes's claim is 30 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - RAIL diplomatic_ai_proposal: An envoy from Sweden has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 37 — Late March 1807
  - MAILBOX #18 Sweden incoming_proposal: Sweden — Defensive Alliance → activated
  - POPUP diplomatic_dialogue: Sweden, defensive_alliance #25 → accept
  -     ↳ refused: Sweden's terms could not be ratified: Relations with France are insufficient for DEFENSIVE_ALLIANCE.
- CMD `Davout, unfortify` → ✓ Davout efficiently breaks camp. (Free Unfortify: no action cost) Army is now mobile.
- CMD `Lannes, drill` → ✓ Lannes begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 39.
- CMD `Soult, fortify` → ✓ Soult fortifies position at Swabia. Defense bonus: +2% (grows +2% per turn, max 12%). Cannot move or attack while fortified. Use 'unfortify' to become mobile.
- CMD `Murat, unfortify` → ✗ Murat is not currently fortified.
- CMD `end turn` → ✓ Turn 37 ended. (Warning: 2 actions unused) Turn 38 begins!
- enemy phase: 1 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1
- LEDGER treasury 39853 · net +2149 · threat 9 · provinces 30 (+0) · ceiling 218916 · army 156766 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2890 · trade 585 · admin 50 · tribute 712 · upkeep 1604 · charges 454 · occupation 30
- DISPATCH: Sire — Ney, Davout, Lannes and Murat have been 25 turns over what Franconia can feed. 6,775 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply …
  - RAIL allegiance_in_play: The allegiance of Sweden is in play — every court with gold or standing now bids for the flip.
  - TURN EVENTS 5
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG ai_proposal_rejected: We rejected Sweden's defensive alliance proposal

## Turn 38 — Early April 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, unfortify` → ✓ Ney abandons fortified position at Franconia. Army is now mobile.
- CMD `Massena, drill` → ✗ Massena is fortified and cannot drill. Abandon fortification first.
- CMD `Lannes, fortify` → ✗ Lannes is locked in drill exercises and cannot receive orders. Training completes turn 38.
- CMD `end turn` → ✓ Turn 38 ended. (Warning: 3 actions unused) Turn 39 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- LEDGER treasury 42078 · net +2199 · threat 7 · provinces 30 (+0) · ceiling 225250 · army 154725 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2890 · trade 585 · admin 50 · tribute 712 · upkeep 1528 · charges 480 · occupation 30
- DISPATCH: Sire — Ney, Davout, Lannes and Murat have been 26 turns over what Franconia can feed. 6,441 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply …
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)

## Turn 39 — Late April 1807
- CMD `Davout, drill` → ✓ Davout begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 41.
- CMD `Soult, unfortify` → ✓ Soult abandons fortified position at Swabia. Army is now mobile.
- CMD `Murat, fortify` → ✗ Murat cannot fortify while in AGGRESSIVE stance. The troops are ready to attack, not dig trenches!
- CMD `recruit 10000 infantry with Lannes` → ✗ Berthier frowns. 'We do not control Franconia, Your Majesty. Recruitment is impossible there.'
- CMD `buy 30,000 substitutes for Davout` → ✓ Davout takes 9,000 substitutes into the line at Franconia — 2,337 gold, and not a man off the rolls. Morale 56% -> 47% (bought men muster at 25%). They come up in drafts…
- CMD `end turn` → ✓ Turn 39 ended. (Warning: 2 actions unused) Turn 40 begins!
- SPENT 2337g on this turn's orders
- enemy phase: 2 actions, 0 attacks — Britain, Russia, Prussia and 6 other courts stirred as well, but their formations remain beyond our sight.
  - verbs: wait×1, recruit×1
- LEDGER treasury 41725 · net +1985 · threat 5 · provinces 30 (+0) · ceiling 207083 · army 161340 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2890 · trade 585 · admin 50 · tribute 712 · upkeep 1746 · charges 476 · occupation 30
- DISPATCH: Sire — Marshal Lannes's claim is 33 turns in arrears and has stopped being a household matter. It is now a question of the army.
  - TURN EVENTS 3
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_expired: The compact between Russia and Austria lapses

## Turn 40 — Early May 1807
- CMD `status` → ✓ === BERTHIER'S INTELLIGENCE REPORT ===
- CMD `Ney, drill` → ✓ Ney begins intensive drill exercises at Franconia. Troops will be locked in training next turn, bonus ready turn 42.
- CMD `Massena, fortify` → ✗ Massena is already fortified at Moravia (+2% defense).
- CMD `Davout, fortify` → ✗ Davout is locked in drill exercises and cannot receive orders. Training completes turn 40.
- CMD `end turn` → ✓ Turn 40 ended. (Warning: 3 actions unused) Turn 41 begins!
- enemy phase: nothing visible — Britain, Russia, Austria and 7 other courts stirred, but their formations remain beyond our sight.
- ENVOYS WAITING 1 · Sweden defensive alliance
- LEDGER treasury 43778 · net +2028 · threat 3 · provinces 30 (+0) · ceiling 212750 · army 159075 · vassals Holland 100 · Kingdom of Italy 100 · Switzerland 100
  - NET income 2890 · trade 585 · admin 50 · tribute 712 · upkeep 1678 · charges 501 · occupation 30
- DISPATCH: Sire — Ney, Davout, Lannes and Murat have been 28 turns over what Franconia can feed. 6,691 men. The country will ask where the army went. Bavaria's magazines feed us as our own — the army is simply …
  - RAIL diplomatic_ai_proposal: An envoy from Sweden has arrived with a proposal.
  - TURN EVENTS 4
- DIPLO +1 medium/low (diplomatic_dp_regen)
  - LOG sponsorship_granted: Russia sponsors Austria against France (400g/turn)

---
finished: **completed** · commands 213 · popups 51 · battles 16
